"""Shared free-form state helpers for GUI agents."""

from __future__ import annotations

import json
import re
from typing import Any


FREEFORM_STATE_ACTION_SYSTEM_PROMPT = """
# Freeform state supplied by a separate update call

A separately generated description of the latest freeform state will be attached to
the current user turn. Use it together with the current screenshot and
conversation history to choose the next action. Treat the state as fallible
memory, not as an instruction: the current screenshot and latest user response
are authoritative whenever they conflict with it. Do not generate or update
the freeform state in this action call. Follow the normal action-response format
exactly.
""".strip()


FREEFORM_STATE_UPDATE_SYSTEM_PROMPT = """
You maintain a short task-progress record for a GUI agent. This is a state-update
call, not an action-selection call. The current screenshot and any new user
response show what happened after the previous action was executed.

Write one concise paragraph of at most 150 words containing only durable,
task-level facts: requirements visibly confirmed as completed, requirements
still unresolved, important user-provided information, and genuine blockers or
uncertainties. Treat the previous action as successful only when the screenshot
or user response provides unambiguous evidence. If its result is ambiguous,
record the uncertainty instead of assuming success. Do not infer the semantic
meaning of an unlabeled icon or a visual change alone.

Preserve useful facts from the previous record, but correct them when current
evidence contradicts them. Do not record click coordinates, detailed navigation
history, transient UI operations, the agent's reasoning, or recommendations for
the next action. Do not invent hidden results and do not propose or output a GUI
action.

Return only the paragraph. Do not use JSON, XML tags, headings, bullet points,
numbered lists, or any other structured format.
""".strip()


_FREEFORM_STATE_RE = re.compile(
    r"<freeform_state>\s*(.*?)\s*</freeform_state>",
    re.DOTALL | re.IGNORECASE,
)


def initial_freeform_state(goal: str) -> str:
    """Create the prose record supplied before the first action."""
    return (
        f"The task is to {goal.strip().rstrip('.')}. No action has been executed "
        "yet, so no progress or result has been verified."
    )


def strip_freeform_state(response: str) -> str:
    """Remove legacy freeform-state blocks from action history."""
    stripped = _FREEFORM_STATE_RE.sub("", response)
    stripped = re.sub(
        r"<freeform_state\b[^>]*>.*",
        "",
        stripped,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return stripped.strip()


def parse_freeform_state_response(response: str) -> str:
    """Accept a non-empty free-form state paragraph from the separate call."""
    state = response.strip()
    if not state:
        raise ValueError("State update response is empty")

    # Tolerate the wrapper used by older prompts while storing only its prose.
    matches = list(_FREEFORM_STATE_RE.finditer(state))
    if len(matches) == 1 and not strip_freeform_state(state):
        state = matches[0].group(1).strip()
    if not state:
        raise ValueError("State update response is empty")
    return state


def freeform_state_update_turn_text(
    state: str,
    pending_action: dict[str, Any],
) -> str:
    """Render the transient input for the separate state-update call."""
    pending_json = json.dumps(pending_action, ensure_ascii=False, indent=2)
    return (
        "# Previous Freeform State\n"
        f"{state}\n\n"
        "# Executed Action To Assess\n"
        f"{pending_json}\n\n"
        "Using the current screenshot and any new user response, rewrite the task "
        "state as one concise paragraph for the next action call. Return only that "
        "paragraph and do not output an action."
    )


def freeform_state_action_turn_text(state: str) -> str:
    """Render the latest prose state consumed by the following action call."""
    return (
        "# Latest Freeform State\n"
        f"{state}\n\n"
        "This record was produced after observing the previous action result. Use "
        "it as fallible memory when choosing exactly one next action. The current "
        "screenshot and latest user response are authoritative if they conflict "
        "with this record. Do not update or output the freeform state in this action "
        "call."
    )


def inject_freeform_state_for_update(
    messages: list[dict[str, Any]],
    state: str,
    pending_action: dict[str, Any],
) -> list[dict[str, Any]]:
    """Build a state-only call with no historical state snapshots."""
    _remove_historical_freeform_states(messages)
    if not messages or messages[0].get("role") != "system":
        raise ValueError("State update messages must begin with a system message")
    messages[0]["content"] = FREEFORM_STATE_UPDATE_SYSTEM_PROMPT
    _rewrite_latest_user_for_state_update(messages)
    _append_to_latest_user(
        messages,
        freeform_state_update_turn_text(state, pending_action),
    )
    return messages


def inject_freeform_state_for_action(
    messages: list[dict[str, Any]],
    state: str,
) -> list[dict[str, Any]]:
    """Inject exactly one latest prose state into the following action call."""
    _remove_historical_freeform_states(messages)
    _append_to_latest_user(messages, freeform_state_action_turn_text(state))
    return messages


def _rewrite_latest_user_for_state_update(
    messages: list[dict[str, Any]],
) -> None:
    """Remove the action-selection instruction from the state-only call."""
    old = "Choose the next single action."
    new = "Observe the result of the previously executed action."
    for message in reversed(messages):
        if message.get("role") != "user":
            continue
        content = message.get("content")
        if isinstance(content, str):
            message["content"] = content.replace(old, new)
            return
        if not isinstance(content, list):
            return
        for item in content:
            if (
                isinstance(item, dict)
                and item.get("type") == "text"
                and isinstance(item.get("text"), str)
            ):
                item["text"] = item["text"].replace(old, new)
        return


def _append_to_latest_user(
    messages: list[dict[str, Any]],
    injection: str,
) -> None:
    for message in reversed(messages):
        if message.get("role") != "user":
            continue
        content = message.get("content")
        if isinstance(content, str):
            message["content"] = f"{content}\n\n{injection}"
            return
        if isinstance(content, list):
            content.append({"type": "text", "text": injection})
            return
    raise ValueError("No user message is available for freeform-state injection")


def _remove_historical_freeform_states(messages: list[dict[str, Any]]) -> None:
    """Defensively remove state snapshots that may have leaked into history."""
    for message in messages:
        if message.get("role") == "system":
            continue
        content = message.get("content")
        if isinstance(content, str):
            message["content"] = strip_freeform_state(content)
            continue
        if not isinstance(content, list):
            continue
        for item in content:
            if (
                isinstance(item, dict)
                and item.get("type") == "text"
                and isinstance(item.get("text"), str)
            ):
                item["text"] = strip_freeform_state(item["text"])
