"""Base agent interface.

Agents observe screenshots and produce actions. The base class is minimal —
no vendor-specific code. Use ``LLMClientMixin`` for OpenAI-compatible API
access.
"""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from typing import Any

from loguru import logger
from openai import OpenAI

from gma.runtime.models import Action, Observation


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    @abstractmethod
    def act(self, observation: Observation) -> Action:
        """Given an observation, decide the next action."""
        ...

    def on_task_start(
        self,
        goal: str,
        app_context: dict[str, str] | None = None,
    ) -> None:
        """Called when a new task begins. Store the goal, app context, reset state, etc."""
        pass

    def on_task_end(self) -> None:
        """Called when a task ends. Clean up agent state."""
        pass

    def on_user_response(self, question: str, response: str) -> None:
        """Called after a task-scoped simulated user answers a call_user action."""
        pass

    @property
    def last_response(self) -> str | None:
        """Return the raw model response produced for the latest action."""
        return None

    @property
    def last_thought(self) -> str | None:
        """Return the model's parsed reasoning for the latest action, if available."""
        return None

    @property
    def task_state(self) -> Any:
        """Return the latest self-maintained task state, when enabled."""
        return None

    @property
    def task_state_mode(self) -> str | None:
        """Return the active task-state mode, when enabled."""
        return None

    @property
    def last_state_response(self) -> str | None:
        """Return the raw response from the latest separate state-update call."""
        return None

    @property
    def last_state_error(self) -> str | None:
        """Return the latest task-state parsing error, when applicable."""
        return None

    @property
    def last_image_caption(self) -> str | None:
        """Return the parsed caption created for an evicted screenshot."""
        return None

    @property
    def last_image_caption_response(self) -> str | None:
        """Return the raw response from the latest image-caption call."""
        return None

    @property
    def last_image_caption_error(self) -> str | None:
        """Return the latest image-caption generation error, when applicable."""
        return None

    @property
    def image_caption_mode(self) -> str | None:
        """Return the active historical image-caption mode, when enabled."""
        return None

    @property
    def stats(self) -> dict[str, Any]:
        """Return agent statistics (token usage, timing, etc.)."""
        return {}


class LLMClientMixin:
    """Mixin for agents that call OpenAI-compatible APIs.

    Provides client setup, endpoint detection, retry logic, and token tracking.
    """

    def setup_llm(self, base_url: str, api_key: str, timeout: float = 120.0) -> None:
        self._llm_client = OpenAI(
            base_url=base_url,
            api_key=api_key or "empty",
            timeout=timeout,
        )
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0
        self._total_cached_tokens = 0
        # Detect the supported endpoint on the first successful request, then
        # reuse it for the lifetime of this client.
        self._llm_api_mode: str | None = None

    def llm_chat(
        self,
        model: str,
        messages: list[dict],
        retries: int = 3,
        **kwargs,
    ) -> str | None:
        """Call an OpenAI-compatible API, detecting Responses when necessary."""
        for attempt in range(retries):
            try:
                if self._llm_api_mode == "responses":
                    resp = self._call_responses(model, messages, kwargs)
                    text = self._responses_text(resp)
                else:
                    try:
                        resp = self._llm_client.chat.completions.create(
                            model=model, messages=messages, **kwargs,
                        )
                        self._llm_api_mode = "chat_completions"
                        text = resp.choices[0].message.content
                    except Exception as chat_error:
                        if self._llm_api_mode is not None or not self._requires_responses(
                            chat_error
                        ):
                            raise
                        logger.info(
                            "Chat Completions endpoint is unavailable; "
                            "switching this LLM client to the Responses API"
                        )
                        resp = self._call_responses(model, messages, kwargs)
                        self._llm_api_mode = "responses"
                        text = self._responses_text(resp)

                self._track_usage(resp)
                return text.strip() if text else None
            except Exception as e:
                logger.warning(f"LLM call failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(1)
        return None

    def _call_responses(self, model: str, messages: list[dict], kwargs: dict):
        params = dict(kwargs)
        if "max_tokens" in params and "max_output_tokens" not in params:
            params["max_output_tokens"] = params.pop("max_tokens")
        return self._llm_client.responses.create(
            model=model,
            input=self._responses_input(messages),
            **params,
        )

    @staticmethod
    def _responses_input(messages: list[dict]) -> list[dict]:
        """Convert Chat Completions image/text parts to Responses input parts."""
        converted = []
        for message in messages:
            content = message.get("content")
            if not isinstance(content, list):
                converted.append({"role": message["role"], "content": content})
                continue

            parts = []
            for part in content:
                if not isinstance(part, dict):
                    parts.append(part)
                    continue
                part_type = part.get("type")
                if part_type == "text":
                    parts.append({"type": "input_text", "text": part.get("text", "")})
                elif part_type == "image_url":
                    image = part.get("image_url")
                    image_url = image.get("url") if isinstance(image, dict) else image
                    converted_image = {"type": "input_image", "image_url": image_url}
                    if isinstance(image, dict) and image.get("detail"):
                        converted_image["detail"] = image["detail"]
                    parts.append(converted_image)
                else:
                    parts.append(part)
            converted.append({"role": message["role"], "content": parts})
        return converted

    @staticmethod
    def _responses_text(response) -> str | None:
        """Read text from both official and lightly compatible Responses clients."""
        output_text = getattr(response, "output_text", None)
        if output_text:
            return output_text

        output = getattr(response, "output", None)
        if output is None and isinstance(response, dict):
            output = response.get("output")
        chunks = []
        for item in output or []:
            content = item.get("content", []) if isinstance(item, dict) else item.content
            for part in content or []:
                part_type = part.get("type") if isinstance(part, dict) else part.type
                if part_type != "output_text":
                    continue
                text = part.get("text") if isinstance(part, dict) else part.text
                if text:
                    chunks.append(text)
        return "".join(chunks) or None

    @staticmethod
    def _requires_responses(error: Exception) -> bool:
        """Return whether an HTTP error says Chat Completions is unsupported."""
        response = getattr(error, "response", None)
        status_code = getattr(error, "status_code", None)
        if status_code is None and response is not None:
            status_code = getattr(response, "status_code", None)

        request = getattr(error, "request", None)
        if request is None and response is not None:
            request = getattr(response, "request", None)
        request_url = str(getattr(request, "url", "")).lower()

        details = [str(error)]
        if response is not None:
            try:
                details.append(json.dumps(response.json(), ensure_ascii=False))
            except Exception:
                try:
                    details.append(response.text)
                except Exception:
                    pass
        message = " ".join(details).lower()

        responses_hint = any(
            hint in message
            for hint in (
                "/responses",
                "responses api",
                "responses endpoint",
                "response api",
            )
        )
        chat_mismatch_hint = any(
            hint in message
            for hint in (
                "chat completions is not supported",
                "chat completions endpoint is not supported",
                "not supported in the chat completions",
                "does not support chat completions",
                "use the responses",
                "use /responses",
            )
        )
        missing_chat_route = (
            status_code in {404, 405, 501}
            and request_url.rstrip("/").endswith("/chat/completions")
        )
        return responses_hint or chat_mismatch_hint or missing_chat_route

    def _track_usage(self, response) -> None:
        usage = getattr(response, "usage", None)
        if usage is None:
            return

        prompt_tokens = getattr(usage, "prompt_tokens", None)
        if prompt_tokens is None:
            prompt_tokens = getattr(usage, "input_tokens", 0)
        completion_tokens = getattr(usage, "completion_tokens", None)
        if completion_tokens is None:
            completion_tokens = getattr(usage, "output_tokens", 0)

        details = getattr(usage, "prompt_tokens_details", None)
        if details is None:
            details = getattr(usage, "input_tokens_details", None)
        cached_tokens = getattr(details, "cached_tokens", 0) if details else 0

        self._total_prompt_tokens += prompt_tokens or 0
        self._total_completion_tokens += completion_tokens or 0
        self._total_cached_tokens += cached_tokens or 0

    def llm_stats(self) -> dict[str, int]:
        return {
            "prompt_tokens": self._total_prompt_tokens,
            "completion_tokens": self._total_completion_tokens,
            "cached_tokens": self._total_cached_tokens,
            "total_tokens": self._total_prompt_tokens + self._total_completion_tokens,
        }

    def reset_llm_stats(self) -> None:
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0
        self._total_cached_tokens = 0
