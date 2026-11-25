"""
Thin, defensive wrapper around the Google Gemini (Generative Language) REST API.

Using the REST endpoint with `requests` keeps dependencies minimal, which makes the
Streamlit deployment simple and reliable. All network/API problems are converted into
a friendly `GeminiError` so the UI can degrade gracefully instead of crashing.
"""

from __future__ import annotations

import json
import os
import time
from typing import Iterable, Iterator

import requests

from .prompt import (
    MAX_OUTPUT_TOKENS,
    MODEL_NAME,
    SYSTEM_PROMPT,
    TEMPERATURE,
    TOP_P,
)

API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
REQUEST_TIMEOUT = 25  # seconds
MAX_HISTORY_MESSAGES = 12  # last 6 turns — enough context without bloating requests
MAX_RETRIES = 2  # for transient 429 / 5xx responses


class GeminiError(Exception):
    """An error that is safe and helpful to display to a visitor."""

    def __init__(self, message: str, hint: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint


def _model_name() -> str:
    """Allow overriding the model via an environment variable / secret."""
    return os.environ.get("GEMINI_MODEL", MODEL_NAME).strip() or MODEL_NAME


def _to_gemini_contents(history: Iterable[dict[str, str]]) -> list[dict]:
    """Map Streamlit's chat roles to Gemini's roles and keep recent history only."""
    contents: list[dict] = []
    for message in list(history)[-MAX_HISTORY_MESSAGES:]:
        role = "model" if message.get("role") == "assistant" else "user"
        text = str(message.get("content", "")).strip()
        if text:
            contents.append({"role": role, "parts": [{"text": text}]})
    return contents


def _build_payload(history: Iterable[dict[str, str]], user_message: str) -> dict:
    contents = _to_gemini_contents(history)
    contents.append({"role": "user", "parts": [{"text": user_message}]})
    return {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": contents,
        "generationConfig": {
            "temperature": TEMPERATURE,
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
            "topP": TOP_P,
        },
    }


def _translate_http_error(status: int) -> GeminiError:
    if status in (400, 401, 403):
        return GeminiError(
            "My API key wasn't accepted just now.",
            "Check that GEMINI_API_KEY is correct and that the Generative Language API "
            "is enabled for the key in Google AI Studio.",
        )
    if status == 404:
        return GeminiError(
            "I couldn't find the language model I use.",
            f"The model '{_model_name()}' isn't available for this key. Older models "
            "such as gemini-2.0-flash have been shut down. Check the model name in "
            "Google AI Studio, or add GEMINI_MODEL to Streamlit Secrets to choose a "
            "supported one (e.g. gemini-3.8-flash).",
        )
    if status == 429:
        return GeminiError(
            "I'm a little busy — the API rate limit was reached.",
            "Wait a few seconds and try again. Free-tier keys have a limited number "
            "of requests per minute.",
        )
    if 500 <= status < 600:
        return GeminiError(
            "The Gemini service is temporarily unavailable.",
            "Please try again in a moment. Your conversation has been kept.",
        )
    return GeminiError(
        f"An unexpected API error occurred (HTTP {status}).",
        "Please try again shortly. If it persists, check your API key setup.",
    )


def _extract_text(data: dict) -> str:
    candidates = data.get("candidates") or []
    if not candidates:
        reason = data.get("promptFeedback", {}).get("blockReason", "")
        hint = f"Prompt was blocked ({reason})." if reason else "No response was returned."
        raise GeminiError("I couldn't produce an answer for that request.", hint)

    candidate = candidates[0]
    if candidate.get("finishReason") == "SAFETY":
        raise GeminiError(
            "I can't answer that one safely.",
            "Try rephrasing your question around furniture or interiors.",
        )

    parts = candidate.get("content", {}).get("parts") or []
    text = "".join(part.get("text", "") for part in parts if isinstance(part, dict)).strip()
    if not text:
        raise GeminiError(
            "I came up empty-handed on that one.",
            "Please try rephrasing your question.",
        )
    return text


def generate_reply(
    api_key: str,
    history: Iterable[dict[str, str]],
    user_message: str,
) -> str:
    """Return Maya's reply. Raises `GeminiError` with a visitor-friendly message."""
    if not api_key or not api_key.strip():
        raise GeminiError(
            "No API key found.",
            "Add GEMINI_API_KEY to Streamlit secrets (or your environment) to enable "
            "the chatbot.",
        )

    url = f"{API_BASE}/{_model_name()}:generateContent"
    params = {"key": api_key.strip()}
    payload = _build_payload(history, user_message)

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(url, params=params, json=payload, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.Timeout:
            raise GeminiError(
                "The design desk took too long to answer.",
                "Check your connection and try again. Your conversation is safe.",
            ) from None
        except requests.exceptions.RequestException:
            raise GeminiError(
                "I couldn't reach the design desk just now.",
                "Check your internet connection and try again.",
            ) from None

        if response.status_code == 200:
            try:
                return _extract_text(response.json())
            except (ValueError, TypeError):
                raise GeminiError(
                    "I got a garbled reply from the service.",
                    "Please try again in a moment.",
                ) from None

        error = _translate_http_error(response.status_code)
        transient = response.status_code == 429 or 500 <= response.status_code < 600
        if transient and attempt < MAX_RETRIES:
            time.sleep(1.5 * (attempt + 1))  # 1.5s, then 3s
            continue
        raise error

    raise GeminiError("Something went wrong. Please try again.")  # pragma: no cover


def generate_reply_stream(
    api_key: str,
    history: Iterable[dict[str, str]],
    user_message: str,
) -> Iterator[str]:
    """Yield reply text chunk-by-chunk using Gemini's SSE streaming endpoint."""
    if not api_key or not api_key.strip():
        raise GeminiError("No API key found.", "Add GEMINI_API_KEY to Streamlit secrets to enable the chatbot.")

    url = f"{API_BASE}/{_model_name()}:streamGenerateContent"
    payload = _build_payload(history, user_message)
    try:
        with requests.post(
            url,
            params={"key": api_key.strip(), "alt": "sse"},
            json=payload,
            timeout=REQUEST_TIMEOUT,
            stream=True,
        ) as response:
            if response.status_code != 200:
                raise _translate_http_error(response.status_code)
            for line in response.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data:"):
                    continue
                try:
                    data = json.loads(line[5:].strip())
                except (ValueError, TypeError):
                    continue
                candidates = data.get("candidates") or []
                if not candidates:
                    continue
                parts = candidates[0].get("content", {}).get("parts") or []
                for part in parts:
                    chunk = part.get("text", "")
                    if chunk:
                        yield chunk
    except GeminiError:
        raise
    except requests.exceptions.RequestException:
        raise GeminiError(
            "I couldn't reach the design desk just now.",
            "Check your connection and try again.",
        ) from None


def generate_structured(
    api_key: str,
    user_message: str,
    schema_description: str,
) -> dict:
    """Ask for JSON output (notebook 'structured outputs' pattern) and parse it."""
    if not api_key or not api_key.strip():
        raise GeminiError("No API key found.", "Add GEMINI_API_KEY to Streamlit secrets to enable the chatbot.")

    instruction = (
        f"{SYSTEM_PROMPT}\n\nOUTPUT FORMAT: Reply with a single valid JSON object only. "
        f"Use exactly these keys: {schema_description}. No prose, no markdown fences."
    )
    payload = {
        "system_instruction": {"parts": [{"text": instruction}]},
        "contents": [{"role": "user", "parts": [{"text": user_message}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 300,
            "responseMimeType": "application/json",
        },
    }
    url = f"{API_BASE}/{_model_name()}:generateContent"
    try:
        response = requests.post(
            url, params={"key": api_key.strip()}, json=payload, timeout=REQUEST_TIMEOUT
        )
    except requests.exceptions.RequestException:
        raise GeminiError("I couldn't reach the design desk just now.", "Check your connection.") from None

    if response.status_code != 200:
        raise _translate_http_error(response.status_code)

    try:
        text = _extract_text(response.json())
        return json.loads(text)
    except (ValueError, TypeError):
        raise GeminiError(
            "I couldn't build a structured answer for that.",
            "Try rephrasing the request.",
        ) from None
