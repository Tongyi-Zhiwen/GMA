"""Shared screenshot-action prompt and response parsing."""

from __future__ import annotations

import base64
import json
from io import BytesIO
from typing import Any

from gma.apps import APP_PACKAGES
from gma.runtime.models import Action, ActionType

ACTION_ALIASES = {
    "click": ["tap", "press", "touch"],
    "long_press": ["hold", "long tap"],
    "input_text": ["type", "enter_text", "write", "enter"],
    "scroll": ["swipe", "fling"],
    "navigate_home": ["home"],
    "navigate_back": ["back"],
    "keyboard_enter": ["enter_key"],
    "open_app": ["open", "launch_app", "launch"],
    "call_user": ["ask_user", "ask user", "clarify", "ask"],
    "wait": ["pause"],
    "status": ["finish", "terminate"],
}

NORMALIZED_ACTIONS: dict[str, str] = {}
for canonical, aliases in ACTION_ALIASES.items():
    NORMALIZED_ACTIONS[canonical] = canonical
    for alias in aliases:
        NORMALIZED_ACTIONS[alias] = canonical
        NORMALIZED_ACTIONS[alias.replace(" ", "_")] = canonical

SYSTEM_PROMPT = """You are a mobile GUI agent operating an Android phone from screenshots.

You must output exactly:
Thought: <one concise sentence>
Action: <one JSON object>

Allowed actions:
- {"action_type":"click","coordinate":[x,y]}
- {"action_type":"double_tap","coordinate":[x,y]}
- {"action_type":"long_press","coordinate":[x,y]}
- {"action_type":"drag","start_coordinate":[x1,y1],"end_coordinate":[x2,y2]}
- {"action_type":"scroll","direction":"up|down|left|right"}
- {"action_type":"input_text","text":"..."}
- {"action_type":"keyboard_enter"}
- {"action_type":"navigate_home"}
- {"action_type":"navigate_back"}
- {"action_type":"open_app","app_name":"exact app name from the available apps list"}
- {"action_type":"call_user","text":"question for the user"}
- {"action_type":"wait"}
- {"action_type":"answer","text":"final answer"}
- {"action_type":"status","goal_status":"complete|infeasible"}

Rules:
- Screen coordinates are relative on a 0-1000 scale, where [0,0] is top-left and [1000,1000] is bottom-right.
- Only output one action each turn.
- Use status complete only when the task is done.
- Use status infeasible only when the task cannot be completed.
- When you believe the task is fully completed, your next action must be {"action_type":"status","goal_status":"complete"}.
- For tasks that ask you to report an answer rather than change the UI, use {"action_type":"answer","text":"..."} as the final action.
- Do not continue interacting with the phone after the task is complete.
- If you need to type text, assume the field is already focused only if it clearly is; otherwise click it first.
- If the screen is loading or transitioning, use wait.
- Use call_user when the goal is ambiguous or missing necessary information. Do not guess required user preferences that are not in the task goal.
- Prefer the shortest reliable path.
"""

QWEN_SYSTEM_PROMPT = (
    SYSTEM_PROMPT
    + "\nAvailable apps:\n"
    + "\n".join(f"- {name}" for name in sorted(APP_PACKAGES) if name != "MallAdmin")
    + "\nOpen an app using its exact name from this list with open_app.\n"
    + "Do not use package names or URLs, and do not invent other app names."
)


def _pil_to_data_url(image) -> str:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _parse_json_fragment(text: str) -> dict[str, Any]:
    """Parse the first complete JSON object, ignoring trailing model output."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            stripped = "\n".join(lines[1:-1]).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        if start >= 0:
            value, _ = json.JSONDecoder().raw_decode(stripped, start)
            return value
        raise


def _split_response(text: str) -> tuple[str, str]:
    """Parse model output into thought and action parts."""
    text = text.strip()
    if "Action:" in text:
        thought_part, action_part = text.split("Action:", 1)
        return thought_part.replace("Thought:", "", 1).strip(), action_part.strip()
    if "Thought:" in text:
        thought_part = text.split("Thought:", 1)[1]
        json_start = thought_part.find("{")
        if json_start >= 0:
            return thought_part[:json_start].strip(), thought_part[json_start:].strip()
        raise ValueError("Model response has Thought but no JSON action")
    if text.startswith("{"):
        return "", text
    json_start = text.find("{")
    if json_start >= 0:
        return text[:json_start].strip(), text[json_start:].strip()
    raise ValueError("Model response contains no valid JSON action")


def _normalize_action_type(action_type: str | None) -> str | None:
    if not action_type:
        return None
    key = action_type.lower().strip().replace(" ", "_")
    return NORMALIZED_ACTIONS.get(key, key)


def _to_absolute(x: float, y: float, width: int, height: int, scale: int) -> tuple[int, int]:
    return int(x * width / scale), int(y * height / scale)


def _action_from_dict(data: dict[str, Any], width: int, height: int, scale_factor: int) -> Action:
    action_type = _normalize_action_type(data.get("action_type"))
    if not action_type:
        raise ValueError("Missing action_type")

    if action_type in {"click", "double_tap", "long_press"}:
        coord = data.get("coordinate")
        if not isinstance(coord, list) or len(coord) != 2:
            raise ValueError(f"{action_type} requires coordinate [x, y]")
        x, y = _to_absolute(coord[0], coord[1], width, height, scale_factor)
        return Action(action_type=ActionType(action_type), x=x, y=y)

    if action_type == "drag":
        start = data.get("start_coordinate")
        end = data.get("end_coordinate")
        if not isinstance(start, list) or len(start) != 2 or not isinstance(end, list) or len(end) != 2:
            raise ValueError("drag requires start_coordinate and end_coordinate")
        start_x, start_y = _to_absolute(start[0], start[1], width, height, scale_factor)
        end_x, end_y = _to_absolute(end[0], end[1], width, height, scale_factor)
        return Action(
            action_type=ActionType.DRAG,
            start_x=start_x,
            start_y=start_y,
            end_x=end_x,
            end_y=end_y,
        )

    if action_type == "scroll":
        return Action(action_type=ActionType.SCROLL, direction=str(data.get("direction", "down")))
    if action_type == "input_text":
        return Action(action_type=ActionType.INPUT_TEXT, text=str(data.get("text", "")))
    if action_type == "open_app":
        return Action(action_type=ActionType.OPEN_APP, app_name=str(data.get("app_name", "")))
    if action_type == "answer":
        return Action(action_type=ActionType.ANSWER, text=str(data.get("text", "")))
    if action_type == "call_user":
        return Action(action_type=ActionType.CALL_USER, text=str(data.get("text", "")))
    if action_type == "status":
        goal_status = str(data.get("goal_status", "")).strip().lower()
        if goal_status == "fail":
            goal_status = "infeasible"
        if goal_status not in {"complete", "infeasible"}:
            raise ValueError(f"Invalid goal_status: {goal_status}")
        return Action(action_type=ActionType.STATUS, goal_status=goal_status)
    if action_type in {"wait", "navigate_home", "navigate_back", "keyboard_enter"}:
        return Action(action_type=ActionType(action_type))
    raise ValueError(f"Unsupported action type: {action_type}")
