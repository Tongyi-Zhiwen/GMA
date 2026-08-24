from __future__ import annotations

import base64
import copy
import json
import re
from io import BytesIO
from typing import Any

from loguru import logger

from gma.agents.base import BaseAgent, LLMClientMixin
from gma.agents.image_caption import (
    IMAGE_CAPTION_CONTEXT_SYSTEM_PROMPT,
    build_image_caption_messages,
    historical_caption_content,
    image_url_from_content,
    parse_image_caption,
    text_from_content,
)
from gma.agents.registry import register_agent
from gma.agents.freeform_state import (
    FREEFORM_STATE_ACTION_SYSTEM_PROMPT,
    initial_freeform_state,
    inject_freeform_state_for_action,
    inject_freeform_state_for_update,
    parse_freeform_state_response,
    strip_freeform_state,
)
from gma.agents.structured_state import (
    append_structured_state_validation_feedback,
    build_structured_state_update_messages,
    inject_structured_state_for_action,
    latest_user_text,
    parse_structured_state_response,
)
from gma.apps import APP_PACKAGES
from gma.runtime.models import Action, ActionType

VISIBLE_APP_NAMES = tuple(sorted(name for name in APP_PACKAGES if name != "MallAdmin"))

CLAUDE_SYSTEM_PROMPT = """# Tools

You may call one function to interact with the Android device. The function signature is provided within <tools></tools> XML tags:
<tools>
{"type":"function","function":{"name_for_human":"mobile_use","name":"mobile_use","description":"Use a touchscreen to interact with a mobile device from screenshots. Perform exactly one action per turn.","parameters":{"properties":{"action":{"description":"The action to perform.","enum":["click","double_click","long_press","swipe","type","system_button","open","wait","call_user","answer","terminate"],"type":"string"},"coordinate":{"description":"Absolute screenshot pixel coordinate [x,y]. Required for click, double_click, long_press, and as the swipe start.","type":"array"},"coordinate2":{"description":"Absolute screenshot pixel coordinate [x,y] for the swipe end.","type":"array"},"text":{"description":"Required for type, open, call_user, and answer.","type":"string"},"time":{"description":"Seconds to wait. Optional for long_press and wait.","type":"number"},"button":{"description":"Required for system_button.","enum":["Back","Home","Enter"],"type":"string"},"status":{"description":"Required for terminate.","enum":["success","failure"],"type":"string"}},"required":["action"],"type":"object"},"args_format":"Format the arguments as a JSON object."}}
</tools>

For each function call, return a JSON object with the function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name":"mobile_use","arguments":<args-json-object>}
</tool_call>

# Response format

Response format for every step:
1) Action: a short imperative describing what to do in the UI.
2) A single <tool_call>...</tool_call> block containing only the mobile_use JSON object.

Examples:
Action: Tap the centered button.
<tool_call>
{"name":"mobile_use","arguments":{"action":"click","coordinate":[500,500]}}
</tool_call>

Action: Open ElementX.
<tool_call>
{"name":"mobile_use","arguments":{"action":"open","text":"ElementX"}}
</tool_call>

Action: Report completion.
<tool_call>
{"name":"mobile_use","arguments":{"action":"terminate","status":"success"}}
</tool_call>

# Available apps

{available_apps}

Use the exact app name from this list with action=open. Do not use package names or URLs, and do not invent other app names.

# Rules

- Output exactly in the order: Action, <tool_call>.
- Output exactly one Action and one mobile_use tool call per turn.
- Coordinates are absolute pixels in the screenshot attached to the current user message.
- Click the center of the intended UI target, not its edge.
- Use action=terminate with status=success only after the task is fully complete.
- Use action=terminate with status=failure only when the task is infeasible.
- For tasks that ask for an answer rather than a UI change, finish with action=answer.
- Use call_user when required task information is missing or ambiguous. Do not guess required user preferences.
- If the screen is loading or transitioning, use wait.
- Do not use actions outside the declared action space.
- Prefer the shortest reliable path.
""".replace("{available_apps}", "\n".join(f"- {name}" for name in VISIBLE_APP_NAMES))


def _pil_to_data_url(image: Any) -> str:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _first_json_object(text: str) -> dict[str, Any]:
    start = text.find("{")
    if start < 0:
        raise ValueError("No JSON object found")

    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:index + 1])
    raise ValueError("Unclosed JSON object")


def parse_mobile_use(text: str) -> tuple[str, dict[str, Any]]:
    """Extract the first mobile_use tool call from a GUIOwl-style response."""
    tool_match = re.search(r"<tool_call>(.*?)</tool_call>", text, re.DOTALL | re.IGNORECASE)
    payload = _first_json_object(tool_match.group(1) if tool_match else text)
    if payload.get("name") != "mobile_use":
        raise ValueError(f"Expected mobile_use tool, got {payload.get('name')!r}")
    arguments = payload.get("arguments")
    if not isinstance(arguments, dict):
        raise ValueError("mobile_use arguments must be a JSON object")
    return str(payload["name"]), arguments


def extract_claude_thought(text: str) -> str | None:
    """Extract explicit reasoning tags, falling back to the Action description."""
    for tag in ("antThinking", "thinking", "think"):
        match = re.search(
            rf"<{tag}>(.*?)</{tag}>",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if match and match.group(1).strip():
            return match.group(1).strip()

    action_match = re.search(
        r"(?:^|\n)Action:\s*(.*?)(?=\s*<tool_call>|$)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if action_match and action_match.group(1).strip():
        return action_match.group(1).strip()
    return None


def _coordinate(
    value: Any,
    width: int,
    height: int,
    coordinate_scale: float = 1.0,
    coordinate_base: float | None = None,
) -> tuple[int, int]:
    if not isinstance(value, list) or len(value) not in {2, 4}:
        raise ValueError(f"Invalid coordinate: {value!r}")
    if len(value) == 4:
        x = (float(value[0]) + float(value[2])) / 2
        y = (float(value[1]) + float(value[3])) / 2
    else:
        x, y = float(value[0]), float(value[1])
    if coordinate_base is not None:
        if coordinate_base <= 0:
            raise ValueError("coordinate_base must be positive")
        scaled_x = round(x * width / coordinate_base)
        scaled_y = round(y * height / coordinate_base)
    else:
        scaled_x = int(x * coordinate_scale)
        scaled_y = int(y * coordinate_scale)
    return (
        max(0, min(width - 1, scaled_x)),
        max(0, min(height - 1, scaled_y)),
    )


def mobile_use_to_action(
    arguments: dict[str, Any],
    width: int,
    height: int,
    coordinate_scale: float = 1.0,
    coordinate_base: float | None = None,
) -> Action:
    action_name = str(arguments.get("action", "")).strip().lower().replace(" ", "_")

    if action_name == "click":
        x, y = _coordinate(
            arguments.get("coordinate"), width, height, coordinate_scale, coordinate_base
        )
        return Action(action_type=ActionType.CLICK, x=x, y=y)
    if action_name == "double_click":
        x, y = _coordinate(
            arguments.get("coordinate"), width, height, coordinate_scale, coordinate_base
        )
        return Action(action_type=ActionType.DOUBLE_TAP, x=x, y=y)
    if action_name == "long_press":
        x, y = _coordinate(
            arguments.get("coordinate"), width, height, coordinate_scale, coordinate_base
        )
        return Action(action_type=ActionType.LONG_PRESS, x=x, y=y)
    if action_name == "swipe":
        start_x, start_y = _coordinate(
            arguments.get("coordinate"),
            width,
            height,
            coordinate_scale,
            coordinate_base,
        )
        end_x, end_y = _coordinate(
            arguments.get("coordinate2"),
            width,
            height,
            coordinate_scale,
            coordinate_base,
        )
        return Action(
            action_type=ActionType.DRAG,
            start_x=start_x,
            start_y=start_y,
            end_x=end_x,
            end_y=end_y,
        )
    if action_name == "type":
        return Action(action_type=ActionType.INPUT_TEXT, text=str(arguments.get("text", "")))
    if action_name == "system_button":
        button = str(arguments.get("button", "")).strip().lower()
        mapping = {
            "back": ActionType.NAVIGATE_BACK,
            "home": ActionType.NAVIGATE_HOME,
            "enter": ActionType.KEYBOARD_ENTER,
        }
        if button not in mapping:
            raise ValueError(f"Unsupported system button: {button!r}")
        return Action(action_type=mapping[button])
    if action_name == "open":
        app_name = str(arguments.get("text", "")).strip()
        if app_name not in VISIBLE_APP_NAMES:
            raise ValueError(f"Unknown app name: {app_name!r}")
        return Action(action_type=ActionType.OPEN_APP, app_name=app_name)
    if action_name == "wait":
        return Action(action_type=ActionType.WAIT)
    if action_name == "call_user":
        return Action(action_type=ActionType.CALL_USER, text=str(arguments.get("text", "")))
    if action_name == "answer":
        return Action(action_type=ActionType.ANSWER, text=str(arguments.get("text", "")))
    if action_name == "terminate":
        status = str(arguments.get("status", "")).strip().lower()
        if status == "success":
            return Action(action_type=ActionType.STATUS, goal_status="complete")
        if status == "failure":
            return Action(action_type=ActionType.STATUS, goal_status="infeasible")
        raise ValueError(f"Invalid terminate status: {status!r}")
    raise ValueError(f"Unsupported mobile_use action: {action_name!r}")


class ClaudeAgent(BaseAgent, LLMClientMixin):
    """GUIOwl-style multimodal agent adapted to GMA's runtime."""

    def __init__(
        self,
        model_name: str,
        llm_base_url: str,
        api_key: str = "empty",
        runtime_conf: dict[str, Any] | None = None,
        last_images: int = 2,
        output_retries: int = 10,
        action_only_history: bool = False,
        caption_old_images: bool = False,
        freeform_state: bool = False,
        structured_state: bool = False,
        claude: str | None = None,
        doubao: str | None = None,
        **_: Any,
    ):
        self.model_name = model_name
        self.llm_base_url = llm_base_url
        self.api_key = api_key
        self.runtime_conf = {
            "temperature": 0.0,
            "max_tokens": 2048,
        }
        if runtime_conf:
            self.runtime_conf.update(runtime_conf)
        self.last_images = max(1, int(last_images))
        self.output_retries = max(1, int(output_retries))
        self.action_only_history = bool(action_only_history)
        self.caption_old_images = bool(caption_old_images)
        self.freeform_state = bool(freeform_state)
        self.structured_state = bool(structured_state)
        if self.freeform_state and self.structured_state:
            raise ValueError(
                "freeform_state and structured_state are mutually exclusive"
            )
        if claude not in {None, "claude"}:
            raise ValueError("claude must be None or 'claude'")
        if doubao not in {None, "doubao"}:
            raise ValueError("doubao must be None or 'doubao'")
        if claude and doubao:
            raise ValueError("claude and doubao coordinate modes are mutually exclusive")
        self.claude = claude == "claude"
        self.doubao = doubao == "doubao"
        self.coordinate_scale = 1.53 if self.claude else 1.0
        self.coordinate_base = 1000.0 if self.doubao else None
        self._goal = ""
        self._messages: list[dict[str, Any]] = []
        self._user_turns: list[dict[str, str]] = []
        self._delivered_user_turns = 0
        self._last_response: str | None = None
        self._last_thought: str | None = None
        self._freeform_state: str | None = None
        self._structured_state: dict[str, Any] | None = None
        self._pending_action: dict[str, Any] | None = None
        self._pending_reasoning: str | None = None
        self._before_action_image_url: str | None = None
        self._last_state_response: str | None = None
        self._last_state_error: str | None = None
        self._last_evicted_image_url: str | None = None
        self._last_image_caption: str | None = None
        self._last_image_caption_response: str | None = None
        self._last_image_caption_error: str | None = None
        self.setup_llm(llm_base_url, api_key)

    def on_task_start(self, goal: str, app_context: dict[str, str] | None = None) -> None:
        del app_context  # ClaudeAgent intentionally receives the complete global app list.
        self._goal = goal
        system_prompt = CLAUDE_SYSTEM_PROMPT
        if self.caption_old_images:
            system_prompt += "\n\n" + IMAGE_CAPTION_CONTEXT_SYSTEM_PROMPT
        if self.freeform_state:
            system_prompt += "\n\n" + FREEFORM_STATE_ACTION_SYSTEM_PROMPT
        self._messages = [{"role": "system", "content": system_prompt}]
        self._user_turns = []
        self._delivered_user_turns = 0
        self._last_response = None
        self._last_thought = None
        self._freeform_state = initial_freeform_state(goal) if self.freeform_state else None
        self._structured_state = None
        self._pending_action = None
        self._pending_reasoning = None
        self._before_action_image_url = None
        self._last_state_response = None
        self._last_state_error = None
        self._last_evicted_image_url = None
        self._last_image_caption = None
        self._last_image_caption_response = None
        self._last_image_caption_error = None
        self.reset_llm_stats()

    def on_task_end(self) -> None:
        self._goal = ""
        self._messages = []
        self._user_turns = []
        self._delivered_user_turns = 0
        self._last_response = None
        self._last_thought = None
        self._freeform_state = None
        self._structured_state = None
        self._pending_action = None
        self._pending_reasoning = None
        self._before_action_image_url = None
        self._last_state_response = None
        self._last_state_error = None
        self._last_evicted_image_url = None
        self._last_image_caption = None
        self._last_image_caption_response = None
        self._last_image_caption_error = None

    def on_user_response(self, question: str, response: str) -> None:
        self._user_turns.append({"question": question, "response": response})

    def _new_user_text(self, width: int, height: int) -> str:
        if len(self._messages) == 1:
            text = (
                f"Task: {self._goal}\n\n"
                f"Current screenshot dimensions: {width}x{height} pixels. "
                "Choose the next single action."
            )
        else:
            text = (
                f"Current screenshot dimensions: {width}x{height} pixels. "
                "Choose the next single action."
            )

        new_turns = self._user_turns[self._delivered_user_turns :]
        if new_turns:
            rendered = "\n".join(
                f"- Agent asked: {turn['question']}\n"
                f"  User answered: {turn['response'] or '[no response]'}"
                for turn in new_turns
            )
            text += (
                "\n\nNew user interaction information:\n"
                f"{rendered}\n"
                "Treat these answers as authoritative task information."
            )
            self._delivered_user_turns = len(self._user_turns)
        return text

    def _trim_old_images(self) -> None:
        image_message_indices = []
        for index, message in enumerate(self._messages):
            content = message.get("content")
            if message.get("role") != "user" or not isinstance(content, list):
                continue
            if any(isinstance(item, dict) and item.get("type") == "image_url" for item in content):
                image_message_indices.append(index)

        for index in image_message_indices[:-self.last_images]:
            content = self._messages[index]["content"]
            image_url = image_url_from_content(content)
            preceding_output = None
            for preceding in reversed(self._messages[:index]):
                if preceding.get("role") == "assistant":
                    preceding_output = text_from_content(preceding.get("content"))
                    break

            if not self.caption_old_images or not image_url:
                self._messages[index]["content"] = [
                    item for item in content
                    if not (
                        isinstance(item, dict)
                        and item.get("type") == "image_url"
                    )
                ]
                self._last_evicted_image_url = image_url
                continue

            caption_messages = build_image_caption_messages(
                goal=self._goal,
                screenshot_image_url=image_url,
                previous_image_url=self._last_evicted_image_url,
                preceding_agent_output=preceding_output,
                observation_text=text_from_content(content),
            )
            caption_conf = dict(self.runtime_conf)
            caption_conf["temperature"] = 0.0
            caption_conf["max_tokens"] = 256
            response = self.llm_chat(
                model=self.model_name,
                messages=caption_messages,
                **caption_conf,
            )
            self._last_image_caption_response = response
            try:
                if not response:
                    raise ValueError("Image caption model returned no response")
                caption = parse_image_caption(response)
                self._last_image_caption = caption
                self._last_image_caption_error = None
                logger.info(f"Claude historical image caption: {caption}")
            except Exception as exc:
                caption = (
                    "The historical screenshot could not be captioned; use the "
                    "surrounding action history instead."
                )
                self._last_image_caption = None
                self._last_image_caption_error = str(exc)
                logger.warning(f"Claude historical image caption failed: {exc}")
            self._messages[index]["content"] = historical_caption_content(
                content,
                caption,
            )
            self._last_evicted_image_url = image_url

    def _append_observation(self, observation: Any) -> None:
        width, height = observation.screenshot.size
        self._messages.append({
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": _pil_to_data_url(observation.screenshot)}},
                {"type": "text", "text": self._new_user_text(width, height)},
            ],
        })
        self._trim_old_images()

    def _messages_for_action_model(self) -> list[dict[str, Any]]:
        messages = copy.deepcopy(self._messages)
        if self.freeform_state and self._freeform_state is not None:
            inject_freeform_state_for_action(messages, self._freeform_state)
        elif self.structured_state and self._structured_state is not None:
            inject_structured_state_for_action(messages, self._structured_state)
        return messages

    def _update_active_state(self, observation: Any) -> None:
        if self.structured_state:
            self._update_structured_state(observation)
            return
        if (
            not self.freeform_state
            or self._freeform_state is None
            or self._pending_action is None
        ):
            return

        messages = copy.deepcopy(self._messages)
        inject_freeform_state_for_update(
            messages,
            self._freeform_state,
            self._pending_action,
        )
        for attempt in range(1, self.output_retries + 1):
            response = self.llm_chat(
                model=self.model_name,
                messages=messages,
                **self.runtime_conf,
            )
            self._last_state_response = response
            if not response:
                self._last_state_error = "State update model returned no response"
                logger.warning(
                    f"Claude state update returned no response "
                    f"({attempt}/{self.output_retries})"
                )
                continue
            try:
                self._freeform_state = parse_freeform_state_response(response)
                self._last_state_error = None
                return
            except Exception as exc:
                self._last_state_error = str(exc)
                logger.warning(
                    f"Invalid Claude state update "
                    f"({attempt}/{self.output_retries}): {exc}"
                )
                logger.debug(response)

    def _update_structured_state(self, observation: Any) -> None:
        if self._pending_action is None or self._before_action_image_url is None:
            return
        messages = build_structured_state_update_messages(
            goal=self._goal,
            previous_state=self._structured_state,
            actor_reasoning=self._pending_reasoning,
            executed_action=self._pending_action,
            before_image_url=self._before_action_image_url,
            after_image_url=_pil_to_data_url(observation.screenshot),
            current_turn_text=latest_user_text(self._messages),
        )
        state_conf = dict(self.runtime_conf)
        state_conf["temperature"] = 0.0
        state_conf["max_tokens"] = 1024
        for attempt in range(1, self.output_retries + 1):
            response = self.llm_chat(
                model=self.model_name,
                messages=messages,
                **state_conf,
            )
            self._last_state_response = response
            if not response:
                self._last_state_error = (
                    "Structured state update model returned no response"
                )
                logger.warning(
                    f"Claude structured state update returned no response "
                    f"({attempt}/{self.output_retries})"
                )
                continue
            try:
                self._structured_state = parse_structured_state_response(response)
                self._last_state_error = None
                return
            except Exception as exc:
                self._last_state_error = str(exc)
                append_structured_state_validation_feedback(
                    messages,
                    self._last_state_error,
                )
                logger.warning(
                    f"Invalid Claude structured state update "
                    f"({attempt}/{self.output_retries}): {exc}"
                )
                logger.debug(response)

    def _remember_action(
        self,
        arguments: dict[str, Any],
        reasoning: str | None,
        observation: Any,
    ) -> None:
        if not (self.freeform_state or self.structured_state):
            return
        self._pending_action = {
            "name": "mobile_use",
            "arguments": copy.deepcopy(arguments),
        }
        if self.structured_state:
            self._pending_reasoning = reasoning or None
            self._before_action_image_url = _pil_to_data_url(observation.screenshot)

    def _assistant_history(self, response: str, arguments: dict[str, Any]) -> str:
        if not self.action_only_history:
            return response
        action_name = str(arguments.get("action", "action")).strip() or "action"
        payload = json.dumps(
            {"name": "mobile_use", "arguments": arguments},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return f"Action: {action_name}.\n<tool_call>{payload}</tool_call>"

    def act(self, observation: Any) -> Action:
        if not self._messages:
            raise RuntimeError("ClaudeAgent.on_task_start must be called before act")

        self._last_response = None
        self._last_thought = None
        self._last_state_response = None
        self._last_state_error = None
        self._last_image_caption = None
        self._last_image_caption_response = None
        self._last_image_caption_error = None
        width, height = observation.screenshot.size
        self._append_observation(observation)
        self._update_active_state(observation)
        attempt_messages = self._messages_for_action_model()
        last_response: str | None = None

        for attempt in range(1, self.output_retries + 1):
            response = self.llm_chat(
                model=self.model_name,
                messages=attempt_messages,
                **self.runtime_conf,
            )
            if not response:
                logger.warning(f"Claude agent returned no response ({attempt}/{self.output_retries})")
                continue
            last_response = response
            state_free_response = strip_freeform_state(response)
            try:
                _, arguments = parse_mobile_use(state_free_response)
                action = mobile_use_to_action(
                    arguments,
                    width,
                    height,
                    coordinate_scale=self.coordinate_scale,
                    coordinate_base=self.coordinate_base,
                )
            except Exception as exc:
                logger.warning(
                    f"Invalid Claude agent output ({attempt}/{self.output_retries}): {exc}"
                )
                repair_instruction = (
                    "Return exactly one supported mobile_use call in <tool_call> "
                    "tags. Do not output task state."
                )
                attempt_messages.extend([
                    {
                        "role": "assistant",
                        "content": state_free_response or "Invalid response omitted.",
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Your previous response was invalid: {exc}. "
                            f"{repair_instruction}"
                        ),
                    },
                ])
                continue

            current_thought = extract_claude_thought(state_free_response)
            self._remember_action(arguments, current_thought, observation)
            self._messages.append({
                "role": "assistant",
                "content": self._assistant_history(state_free_response, arguments),
            })
            self._last_response = response
            self._last_thought = current_thought
            logger.info(f"Claude agent action: {arguments}")
            return action

        if last_response:
            logger.debug(last_response)
            self._last_response = last_response
            self._last_thought = extract_claude_thought(strip_freeform_state(last_response))
        logger.warning("Claude agent exhausted output retries; waiting")
        wait_arguments = {"action": "wait"}
        self._remember_action(
            wait_arguments,
            "No valid model response was available, so wait.",
            observation,
        )
        self._messages.append({
            "role": "assistant",
            "content": self._assistant_history(
                "Action: Wait and inspect the next screen.\n"
                '<tool_call>{"name":"mobile_use","arguments":{"action":"wait"}}</tool_call>',
                wait_arguments,
            ),
        })
        return Action(action_type=ActionType.WAIT)

    @property
    def last_response(self) -> str | None:
        return self._last_response

    @property
    def last_thought(self) -> str | None:
        return self._last_thought

    @property
    def task_state(self) -> str | dict[str, Any] | None:
        if self.structured_state:
            return copy.deepcopy(self._structured_state)
        return self._freeform_state

    @property
    def task_state_mode(self) -> str | None:
        if self.structured_state:
            return "structured"
        if self.freeform_state:
            return "freeform"
        return None

    @property
    def last_state_response(self) -> str | None:
        return self._last_state_response

    @property
    def last_state_error(self) -> str | None:
        return self._last_state_error

    @property
    def last_image_caption(self) -> str | None:
        return self._last_image_caption

    @property
    def last_image_caption_response(self) -> str | None:
        return self._last_image_caption_response

    @property
    def last_image_caption_error(self) -> str | None:
        return self._last_image_caption_error

    @property
    def image_caption_mode(self) -> str | None:
        return "evicted_screenshot" if self.caption_old_images else None

    @property
    def stats(self) -> dict[str, Any]:
        return self.llm_stats()


register_agent("claude_agent", ClaudeAgent)
