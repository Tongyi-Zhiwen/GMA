"""Helpers for replacing evicted GUI screenshots with textual captions."""

from __future__ import annotations

import re
from typing import Any

IMAGE_CAPTION_CONTEXT_SYSTEM_PROMPT = """
# Historical screenshot captions

Some older screenshots in the conversation may be replaced by explicitly
labelled historical captions. Use them as fallible memory of earlier GUI
states. Never ground a click or other coordinate action against a historical
caption or an image described by one; ground actions only against the latest
current screenshot. The current screenshot and latest user response are
authoritative when they conflict with historical memory.
""".strip()


IMAGE_CAPTION_SYSTEM_PROMPT = """
You caption an earlier GUI observation for a computer-use agent. This is a
memory-compression call, not an action-selection call.

Describe only task-relevant facts visibly supported by the screenshot being
captioned. When a preceding screenshot and executed agent output are supplied,
use them only to identify the observed result of that action. Preserve the app
or page, important visible values and selections, results, dialogs, errors,
confirmations, and unresolved UI state that could matter later.

Do not recommend a next action, expose chain-of-thought, repeat click
coordinates, infer hidden success, or describe decorative layout. Do not treat
the preceding agent's expectation as evidence. Return one concise paragraph of
at most 80 words and no heading, JSON, XML, bullets, or preamble.
""".strip()


_CURRENT_ACTION_REQUEST_RE = re.compile(
    r"Current screenshot dimensions:\s*\d+x\d+ pixels\.\s*"
    r"Choose the next single action\.?",
    flags=re.IGNORECASE,
)
_CAPTION_WRAPPER_RE = re.compile(
    r"^<caption>\s*(.*?)\s*</caption>$",
    flags=re.IGNORECASE | re.DOTALL,
)


def build_image_caption_messages(
    *,
    goal: str,
    screenshot_image_url: str,
    previous_image_url: str | None,
    preceding_agent_output: str | None,
    observation_text: str,
) -> list[dict[str, Any]]:
    """Build a separate multimodal call for one historical observation."""
    content: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                f"# Original Task\n{goal}\n\n"
                "The images below are historical evidence. Caption the second "
                "image when two images are present; otherwise caption the only "
                "image."
            ),
        }
    ]
    if previous_image_url:
        content.extend([
            {"type": "text", "text": "# Preceding Screenshot"},
            {"type": "image_url", "image_url": {"url": previous_image_url}},
        ])
    if preceding_agent_output:
        content.append({
            "type": "text",
            "text": (
                "# Executed Agent Output Before The Screenshot\n"
                f"{preceding_agent_output[:6000]}"
            ),
        })
    content.extend([
        {"type": "text", "text": "# Screenshot To Caption"},
        {"type": "image_url", "image_url": {"url": screenshot_image_url}},
    ])
    stable_text = stable_observation_text(observation_text)
    if stable_text:
        content.append({
            "type": "text",
            "text": (
                "# Durable Text Attached To This Observation\n"
                f"{stable_text}\n\n"
                "Return only the concise historical screenshot caption."
            ),
        })
    else:
        content.append({
            "type": "text",
            "text": "Return only the concise historical screenshot caption.",
        })
    return [
        {"role": "system", "content": IMAGE_CAPTION_SYSTEM_PROMPT},
        {"role": "user", "content": content},
    ]


def parse_image_caption(response: str) -> str:
    """Normalize a caption response and enforce a compact text budget."""
    caption = response.strip()
    wrapper = _CAPTION_WRAPPER_RE.match(caption)
    if wrapper:
        caption = wrapper.group(1).strip()
    caption = " ".join(caption.split())
    if not caption:
        raise ValueError("Image caption response is empty")

    words = caption.split()
    if len(words) > 100:
        caption = " ".join(words[:100]).rstrip(" ,;:") + "…"
    if len(caption) > 1200:
        caption = caption[:1199].rstrip(" ,;:") + "…"
    return caption


def image_url_from_content(content: Any) -> str | None:
    """Return the first image URL from a multimodal message content list."""
    if not isinstance(content, list):
        return None
    for item in content:
        if not isinstance(item, dict) or item.get("type") != "image_url":
            continue
        image = item.get("image_url")
        if isinstance(image, dict):
            url = image.get("url")
        else:
            url = image
        if isinstance(url, str) and url:
            return url
    return None


def text_from_content(content: Any) -> str:
    """Join text parts from a string or multimodal message content list."""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return "\n".join(
        str(item.get("text", ""))
        for item in content
        if isinstance(item, dict) and item.get("type") == "text"
    ).strip()


def stable_observation_text(text: str) -> str:
    """Remove the obsolete current-screen action request from old turns."""
    stable = _CURRENT_ACTION_REQUEST_RE.sub("", text)
    stable = re.sub(r"\n{3,}", "\n\n", stable).strip()
    return stable


def historical_caption_content(original_content: Any, caption: str) -> list[dict[str, str]]:
    """Replace an image observation with correctly labelled historical text."""
    stable_text = stable_observation_text(text_from_content(original_content))
    parts = []
    if stable_text:
        parts.append(stable_text)
    parts.append(
        "# Historical Screenshot Caption\n"
        "This describes an earlier screen and must not be used for current "
        "coordinate grounding.\n"
        f"{caption}"
    )
    return [{"type": "text", "text": "\n\n".join(parts)}]
