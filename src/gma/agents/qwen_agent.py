from __future__ import annotations

import copy
import json
from typing import Any

from loguru import logger

from gma.agents.base import BaseAgent, LLMClientMixin
from gma.agents.action_protocol import (
    QWEN_SYSTEM_PROMPT,
    _action_from_dict,
    _parse_json_fragment,
    _pil_to_data_url,
    _split_response,
)
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
from gma.runtime.models import Action, ActionType


class QwenAgent(BaseAgent, LLMClientMixin):
    """Screenshot action protocol with persistent conversation context."""

    def __init__(
        self,
        model_name: str,
        llm_base_url: str,
        api_key: str = "empty",
        runtime_conf: dict[str, Any] | None = None,
        scale_factor: int = 1000,
        last_images: int = 2,
        action_only_history: bool = False,
        caption_old_images: bool = False,
        freeform_state: bool = False,
        structured_state: bool = False,
        output_retries: int = 3,
        **_: Any,
    ):
        self.model_name = model_name
        self.llm_base_url = llm_base_url
        self.api_key = api_key
        self.freeform_state = bool(freeform_state)
        self.structured_state = bool(structured_state)
        if self.freeform_state and self.structured_state:
            raise ValueError(
                "freeform_state and structured_state are mutually exclusive"
            )
        self.runtime_conf = {
            "temperature": 0.0,
            "max_tokens": 2048 if self.freeform_state else 1024,
        }
        if runtime_conf:
            self.runtime_conf.update(runtime_conf)
        self.scale_factor = scale_factor
        self.last_images = max(1, int(last_images))
        self.action_only_history = bool(action_only_history)
        self.caption_old_images = bool(caption_old_images)
        self.output_retries = max(1, int(output_retries))
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
        del app_context  # The prompt intentionally exposes the complete global app list.
        self._goal = goal
        system_prompt = QWEN_SYSTEM_PROMPT
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
                f"Current task goal: {self._goal}\n\n"
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
            if any(
                isinstance(item, dict) and item.get("type") == "image_url"
                for item in content
            ):
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
                    item
                    for item in content
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
                logger.info(f"Qwen historical image caption: {caption}")
            except Exception as exc:
                caption = (
                    "The historical screenshot could not be captioned; use the "
                    "surrounding action history instead."
                )
                self._last_image_caption = None
                self._last_image_caption_error = str(exc)
                logger.warning(f"Qwen historical image caption failed: {exc}")
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
                {
                    "type": "image_url",
                    "image_url": {"url": _pil_to_data_url(observation.screenshot)},
                },
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
                    f"Qwen state update returned no response "
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
                    f"Invalid Qwen state update "
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
                    f"Qwen structured state update returned no response "
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
                    f"Invalid Qwen structured state update "
                    f"({attempt}/{self.output_retries}): {exc}"
                )
                logger.debug(response)

    def _remember_action(
        self,
        action_dict: dict[str, Any],
        reasoning: str | None,
        observation: Any,
    ) -> None:
        if not (self.freeform_state or self.structured_state):
            return
        self._pending_action = copy.deepcopy(action_dict)
        if self.structured_state:
            self._pending_reasoning = reasoning or None
            self._before_action_image_url = _pil_to_data_url(observation.screenshot)

    def _assistant_history(self, response: str, action_dict: dict[str, Any]) -> str:
        if not self.action_only_history:
            return response
        return "Action: " + json.dumps(
            action_dict,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    def act(self, observation: Any) -> Action:
        if not self._messages:
            raise RuntimeError("QwenAgent.on_task_start must be called before act")

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
        attempt_limit = self.output_retries if self.freeform_state else 1
        last_response: str | None = None

        for attempt in range(1, attempt_limit + 1):
            response = self.llm_chat(
                model=self.model_name,
                messages=attempt_messages,
                **self.runtime_conf,
            )
            if not response:
                logger.warning(
                    f"Qwen agent returned no response ({attempt}/{attempt_limit})"
                )
                continue

            last_response = response
            state_free_response = strip_freeform_state(response)
            try:
                thought, action_blob = _split_response(state_free_response)
                action_dict = _parse_json_fragment(action_blob)
                action = _action_from_dict(
                    action_dict,
                    width,
                    height,
                    self.scale_factor,
                )
            except Exception as exc:
                logger.warning(
                    f"Invalid Qwen agent output ({attempt}/{attempt_limit}): {exc}"
                )
                logger.debug(response)
                if not self.freeform_state:
                    action_dict = {"action_type": "wait"}
                    self._last_response = response
                    self._remember_action(action_dict, None, observation)
                    self._messages.append({
                        "role": "assistant",
                        "content": self._assistant_history(response, action_dict),
                    })
                    return Action(action_type=ActionType.WAIT)

                if attempt < attempt_limit:
                    attempt_messages.extend([
                        {
                            "role": "assistant",
                            "content": state_free_response or "Invalid response omitted.",
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Your previous response was invalid: {exc}. "
                                "Return Thought followed by exactly one Action JSON "
                                "object. Do not output task state."
                            ),
                        },
                    ])
                continue

            self._remember_action(action_dict, thought or None, observation)
            self._last_response = response
            self._last_thought = thought or None
            self._messages.append({
                "role": "assistant",
                "content": self._assistant_history(state_free_response, action_dict),
            })
            logger.info(f"Qwen agent thought: {thought}")
            logger.info(f"Qwen agent action: {action_dict}")
            return action

        if last_response:
            self._last_response = last_response
            state_free_response = strip_freeform_state(last_response)
            try:
                thought, _ = _split_response(state_free_response)
                self._last_thought = thought or None
            except Exception:
                pass
        logger.warning("Qwen agent exhausted output retries; waiting")
        wait_action = {"action_type": "wait"}
        self._remember_action(
            wait_action,
            "No valid model response was available, so wait.",
            observation,
        )
        self._messages.append({
            "role": "assistant",
            "content": self._assistant_history(
                "Thought: No valid model response was available, so wait.\n"
                'Action: {"action_type":"wait"}',
                wait_action,
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


register_agent("qwen_agent", QwenAgent)
