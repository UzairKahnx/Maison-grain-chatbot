"""
Maison & Grain domain chatbot engine — notebook-style implementation.

This file follows the structure taught in the class lab notebook:
  · secure API-key loading with secrets / environment / prompt fallbacks
  · token counting and latency measurement
  · role-based system prompt, few-shot examples and model parameters
  · a memory class that keeps and truncates conversation history
  · input guardrails and graceful error handling
  · streaming and structured (JSON) output helpers
  · an interactive command-line chatbot

Adapted from the OpenAI examples in the notebook to the Google Gemini API, with the
domain changed from a generic coding assistant to a furniture showroom consultant.
The exact same engine is used by app.py (Streamlit).

Run:  python chatbot.py --demo       # no key needed
      python chatbot.py               # live Gemini (key from secrets / env / prompt)
"""

from __future__ import annotations

import argparse
import os
import time
from getpass import getpass
from typing import Iterator

from src.demo import demo_reply
from src.gemini_client import (
    GeminiError,
    generate_reply,
    generate_reply_stream,
    generate_structured,
)
from src.prompt import SYSTEM_PROMPT, WELCOME_MESSAGE

# ---------------------------------------------------------------------------
# 1. Secure credential loading
# ---------------------------------------------------------------------------
def load_api_key(interactive: bool = True) -> str:
    """Secrets → environment variable → hidden prompt. Never hard-code a key."""
    try:
        import streamlit as st  # optional outside the Streamlit app

        try:
            value = st.secrets.get("GEMINI_API_KEY", "") if st.secrets else ""
        except Exception:
            value = ""
        if value and "paste-your-key" not in str(value):
            return str(value).strip()
    except ImportError:
        pass

    value = os.environ.get("GEMINI_API_KEY", "").strip()
    if value:
        return value

    if interactive:
        try:
            value = getpass("Enter your Gemini API key (input hidden): ").strip()
        except (EOFError, KeyboardInterrupt):
            return ""
        if value:
            os.environ["GEMINI_API_KEY"] = value
        return value
    return ""


# ---------------------------------------------------------------------------
# 2. Token counting (tiktoken when available, safe approximation otherwise)
# ---------------------------------------------------------------------------
try:  # notebook uses tiktoken; install it for exact counts if you wish
    import tiktoken

    _ENCODER = tiktoken.get_encoding("o200k_base")
except Exception:  # pragma: no cover - optional dependency
    _ENCODER = None


def count_tokens(text: str) -> int:
    """Approximate token count, mirroring the notebook's token-inspection section."""
    if _ENCODER is not None:
        return len(_ENCODER.encode(text))
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# 3. Guardrails
# ---------------------------------------------------------------------------
BANNED_PATTERNS = (
    "ignore previous instructions",
    "bypass instructions",
    "disregard your instructions",
    "reveal your system prompt",
    "reveal your instructions",
    "pretend you are a different",
)

SECURITY_REPLY = (
    "I can't change the rules I work under, but I'm happy to help with furniture, "
    "materials, sizing or styling. What are you looking for?"
)

OFF_TOPIC_WORDS = (
    "weather", "football", "cricket", "politics", "president", "election", "homework",
    "python", "javascript", "coding", "recipe", "movie", "celebrity", "stock",
    "doctor", "lawyer", "lawsuit", "translate", "math problem",
)
DOMAIN_WORDS = (
    "sofa", "couch", "chair", "table", "lamp", "furniture", "fabric", "leather",
    "oak", "bouclé", "boucle", "delivery", "warranty", "room", "style", "colour",
    "color", "decor", "care", "clean", "size", "measure", "price", "budget",
)


def is_off_topic(text: str) -> bool:
    """True only when off-topic words appear with no furniture-related words."""
    lowered = text.lower()
    return (
        any(word in lowered for word in OFF_TOPIC_WORDS)
        and not any(word in lowered for word in DOMAIN_WORDS)
    )


# ---------------------------------------------------------------------------
# 4. Memory chatbot class (notebook Section 8, extended)
# ---------------------------------------------------------------------------
class FurnitureChatbot:
    """A domain-focused assistant with memory, guardrails and usage tracking."""

    def __init__(
        self,
        api_key: str = "",
        system_instruction: str = SYSTEM_PROMPT,
        max_history_turns: int = 6,
        demo_mode: bool = False,
    ) -> None:
        self.api_key = api_key
        self.max_history_turns = max_history_turns
        self.demo_mode = demo_mode
        self.history: list[dict[str, str]] = [
            {"role": "system", "content": system_instruction},
            {"role": "assistant", "content": WELCOME_MESSAGE},
        ]
        self.stats = {"requests": 0, "prompt_tokens": 0, "completion_tokens": 0, "last_latency": 0.0}

    # -- memory helpers -----------------------------------------------------
    def recent_history(self) -> list[dict[str, str]]:
        """Only the last N turns are sent — token optimisation from the notebook."""
        turns = self.max_history_turns * 2
        return self.history[1:][-turns:]

    def messages_for_display(self) -> list[dict[str, str]]:
        """Conversation without the hidden system instruction."""
        return list(self.history[1:])

    def reset(self) -> None:
        """Keep the persona and greeting, forget everything else."""
        self.history = self.history[:2]

    # -- guardrail ----------------------------------------------------------
    def _guardrail(self, text: str) -> str:
        lowered = text.lower()
        if any(pattern in lowered for pattern in BANNED_PATTERNS):
            return SECURITY_REPLY
        return ""

    # -- main chat ----------------------------------------------------------
    def chat(self, user_input: str, context: str = "") -> str:
        """Send one turn, remember it, and return the assistant's reply."""
        message = user_input.strip()
        if not message:
            return "Please tell me a little about what you're looking for."

        blocked = self._guardrail(message)
        if blocked:
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": blocked})
            return blocked

        recent = self.recent_history()  # history *before* this message
        self.history.append({"role": "user", "content": message})

        started = time.perf_counter()
        try:
            if self.demo_mode:
                reply = demo_reply(context + message)
            else:
                reply = generate_reply(self.api_key, recent, context + message)
        except GeminiError:
            self.history.pop()  # don't keep an unanswered question in memory
            raise

        elapsed = time.perf_counter() - started
        self.history.append({"role": "assistant", "content": reply})
        self.stats["requests"] += 1
        self.stats["prompt_tokens"] += count_tokens(context + message)
        self.stats["completion_tokens"] += count_tokens(reply)
        self.stats["last_latency"] = elapsed
        return reply

    # -- streaming (notebook Section 10) ------------------------------------
    def chat_stream(self, user_input: str, context: str = "") -> Iterator[str]:
        """Yield chunks as they arrive, then store the complete reply in memory."""
        message = user_input.strip()
        blocked = self._guardrail(message)
        if blocked:
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": blocked})
            yield blocked
            return

        recent = self.recent_history()
        self.history.append({"role": "user", "content": message})
        started = time.perf_counter()
        collected: list[str] = []

        try:
            if self.demo_mode:
                for chunk in demo_reply(context + message).split(" "):
                    collected.append(chunk)
                    yield chunk + " "
            else:
                for chunk in generate_reply_stream(self.api_key, recent, context + message):
                    collected.append(chunk)
                    yield chunk
        except GeminiError:
            self.history.pop()
            raise

        reply = "".join(collected).strip()
        if reply:
            self.history.append({"role": "assistant", "content": reply})
        self.stats["requests"] += 1
        self.stats["last_latency"] = time.perf_counter() - started

    # -- structured output (notebook Section 9) -----------------------------
    def structured_reply(self, user_input: str, schema_description: str) -> dict:
        """Return a JSON object, e.g. classified service/enquiry requests."""
        return generate_structured(self.api_key, user_input, schema_description)

    # -- reporting ----------------------------------------------------------
    def report(self) -> str:
        s = self.stats
        return (
            f"Requests: {s['requests']} · Prompt tokens (approx.): {s['prompt_tokens']} · "
            f"Reply tokens (approx.): {s['completion_tokens']} · "
            f"Last reply: {s['last_latency']:.2f}s"
        )


# ---------------------------------------------------------------------------
# 5. Interactive command-line chatbot (notebook Sections 7 & 8)
# ---------------------------------------------------------------------------
def talk_to_bot(demo_mode: bool = False, stream: bool = False) -> None:
    # Windows consoles often default to cp1252, which cannot print our emojis.
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    key = "" if demo_mode else load_api_key()
    if not demo_mode and not key:
        print("No API key available — switching to Demo mode.")
        demo_mode = True
    bot = FurnitureChatbot(api_key=key, demo_mode=demo_mode)
    print("Maya (Maison & Grain) ready. Type 'exit' to quit, 'reset' to clear memory.\n")

    while True:
        try:
            user_msg = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if user_msg.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        if user_msg.lower() == "reset":
            bot.reset()
            print("Memory cleared. Starting over.\n")
            continue
        if not user_msg:
            continue

        print("Maya: ", end="", flush=True)
        try:
            if stream:
                for chunk in bot.chat_stream(user_msg):
                    print(chunk, end="", flush=True)
                print()
            else:
                print(bot.chat(user_msg))
        except GeminiError as error:
            print(f"\n[Couldn't complete that: {error.message} {error.hint}]\n")
        print(f"  ({bot.report()})\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Maison & Grain furniture chatbot")
    parser.add_argument("--demo", action="store_true", help="use sample replies, no API key")
    parser.add_argument("--stream", action="store_true", help="stream replies chunk by chunk")
    args = parser.parse_args()
    talk_to_bot(demo_mode=args.demo, stream=args.stream)


if __name__ == "__main__":
    main()
