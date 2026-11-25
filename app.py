"""
Maison & Grain — furniture showroom design concierge.

A domain-focused chatbot powered by Google Gemini (Google AI Studio API key).
Behaviour is driven mainly by the system prompt in `src/prompt.py`.

Run locally:   streamlit run app.py
Deploy:        Streamlit Community Cloud (see README.md)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from chatbot import FurnitureChatbot
from src.gemini_client import GeminiError
from src.prompt import (
    ASSISTANT_NAME,
    MAX_OUTPUT_TOKENS,
    MODEL_NAME,
    STORE_NAME,
    SUGGESTED_PROMPTS,
    TEMPERATURE,
    TOP_P,
)
from src.ui import (
    apply_custom_css,
    render_brand,
    render_collection,
    render_hero,
    render_trust_bar,
)

st.set_page_config(
    page_title="Maison & Grain | Design Concierge",
    page_icon="🛋️",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_custom_css()


# ---------------------------------------------------------------------------
# State & configuration helpers
# ---------------------------------------------------------------------------
def _secret_key() -> str:
    """Read the key from Streamlit secrets or an environment variable."""
    try:
        value = st.secrets.get("GEMINI_API_KEY", "") if st.secrets else ""
    except Exception:
        value = ""
    if value and str(value).strip() and "paste-your-key" not in str(value):
        return str(value).strip()
    return os.environ.get("GEMINI_API_KEY", "").strip()


def _secret_value(name: str) -> str:
    """Read a non-API secret from Streamlit secrets or the environment."""
    try:
        value = st.secrets.get(name, "") if st.secrets else ""
    except Exception:
        value = ""
    if value and str(value).strip():
        return str(value).strip()
    return os.environ.get(name, "").strip()


def _init_state() -> None:
    st.session_state.setdefault("bot", FurnitureChatbot())
    st.session_state.setdefault("pending_prompt", "")
    st.session_state.setdefault("local_api_key", "")
    st.session_state.setdefault("authorized", False)
    st.session_state.setdefault("demo_mode", not bool(_secret_key() or st.session_state.get("local_api_key")))


_init_state()
_secret = _secret_key()
_local_key = str(st.session_state.get("local_api_key", "")).strip()
api_key = _secret or _local_key
access_code = _secret_value("APP_ACCESS_CODE")


# ---------------------------------------------------------------------------
# Optional access gate — keeps the public app (and your API quota) private
# ---------------------------------------------------------------------------
if access_code and not st.session_state.authorized:
    st.markdown(
        f"""
        <div class="mg-hero">
          <div class="mg-hero-content">
            <div class="mg-eyebrow">Private showroom preview</div>
            <h1>Welcome back.</h1>
            <p>This design concierge is invite-only. Enter your access code to continue.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("showroom_access"):
        submitted_code = st.text_input("Access code", type="password", placeholder="Enter your code")
        unlocked = st.form_submit_button("Enter the showroom", use_container_width=True)
    if unlocked:
        if submitted_code.strip() == access_code:
            st.session_state.authorized = True
            st.rerun()
        else:
            st.error("That code isn't right. Please try again.")
    st.stop()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    render_brand()
    st.caption("Your personal design concierge.")

    if st.session_state.demo_mode:
        st.markdown('<span class="mg-badge mg-badge-demo">● DEMO MODE</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="mg-badge mg-badge-live">● LIVE · GEMINI</span>', unsafe_allow_html=True)

    if access_code:
        st.markdown('<span class="mg-badge mg-badge-demo">🔒 INVITE ONLY</span>', unsafe_allow_html=True)

    st.markdown('<div class="mg-side-label">Connection</div>', unsafe_allow_html=True)
    if not _secret:
        st.text_input(
            "Gemini API key (local testing)",
            type="password",
            key="local_api_key",
            help="Paste a key from https://aistudio.google.com/apikey. On Streamlit Cloud, use secrets instead.",
            placeholder="AIza…",
        )
        st.markdown(
            '<div class="mg-note">For deployment, add the key to '
            '<b>.streamlit/secrets.toml</b> or the app\'s Secrets settings — never '
            'commit it to your repository.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="mg-note">API key loaded from Streamlit secrets. 🔒</div>', unsafe_allow_html=True)

    demo_toggle = st.toggle(
        "Demo mode (no API key needed)",
        value=bool(st.session_state.demo_mode),
        help="Try the interface with built-in sample replies before connecting Gemini.",
    )
    st.session_state.demo_mode = bool(demo_toggle)
    if not demo_toggle and not api_key:
        st.warning("Add an API key above, or keep Demo mode on.")

    st.markdown('<div class="mg-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="mg-side-label">Your preferences</div>', unsafe_allow_html=True)
    room = st.selectbox(
        "Room",
        ["Not specified", "Living room", "Dining room", "Bedroom", "Home office", "Other"],
    )
    style = st.selectbox(
        "Style",
        ["Not specified", "Modern", "Scandinavian", "Japandi", "Mid-century", "Traditional", "Eclectic"],
    )
    budget = st.selectbox(
        "Indicative budget",
        ["Not specified", "Under $1,000", "$1,000 – $2,500", "$2,500 – $5,000", "$5,000+"],
    )

    context_bits = []
    if room != "Not specified":
        context_bits.append(f"Room: {room}")
    if style != "Not specified":
        context_bits.append(f"Style: {style}")
    if budget != "Not specified":
        context_bits.append(f"Budget: {budget}")
    visitor_context = f"[Visitor context — {'; '.join(context_bits)}] " if context_bits else ""

    with st.expander("🪑 Collection highlights"):
        render_collection()

    with st.expander("⚙️ About Maya & model settings"):
        st.markdown(
            f"""
            <div class="mg-config">
              <b>Role.</b> Maya is a senior interior design consultant at {STORE_NAME}:
              warm, knowledgeable and concise.<br/><br/>
              <b>Context &amp; guardrail.</b> Furniture and interiors only. Off-topic
              questions are politely redirected; catalogue facts come from the system
              prompt, never invented.<br/><br/>
              <b>Model.</b> <code>{MODEL_NAME}</code> via the Google Gemini API<br/>
              <b>Temperature.</b> <code>{TEMPERATURE}</code> — accurate product facts
              with a natural, friendly tone.<br/>
              <b>Max tokens.</b> <code>{MAX_OUTPUT_TOKENS}</code> — keeps replies short
              and scannable in a chat window.<br/>
              <b>Top-p.</b> <code>{TOP_P}</code> — mild sampling for polished wording.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Full prompt design: src/prompt.py · Engine: chatbot.py")

    st.markdown('<div class="mg-divider"></div>', unsafe_allow_html=True)
    if st.button("🔄 Start a fresh conversation", use_container_width=True):
        st.session_state.bot.reset()
        st.session_state.pending_prompt = ""
        st.rerun()

    if access_code and st.button("🔒 Lock this conversation", use_container_width=True):
        st.session_state.authorized = False
        st.session_state.bot.reset()
        st.rerun()

# Point the engine at the current key / mode before handling any messages.
bot: FurnitureChatbot = st.session_state.bot
bot.api_key = api_key
bot.demo_mode = bool(st.session_state.demo_mode)


# ---------------------------------------------------------------------------
# Main conversation area
# ---------------------------------------------------------------------------
render_hero()
render_trust_bar()

messages: list[dict[str, str]] = bot.messages_for_display()
for message in messages:
    avatar = "🛋️" if message["role"] == "assistant" else "🙂"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Quick-start suggestions (shown near the beginning of a conversation)
if len(messages) <= 3:
    st.markdown(
        '<div class="mg-section-sub" style="margin-top:20px">Not sure where to start? Try one of these:</div>',
        unsafe_allow_html=True,
    )
    suggestion_columns = st.columns(2)
    for index, prompt_text in enumerate(SUGGESTED_PROMPTS):
        if suggestion_columns[index % 2].button(
            prompt_text, key=f"suggestion_{index}", use_container_width=True
        ):
            st.session_state.pending_prompt = prompt_text
            st.rerun()

user_input = st.chat_input("Ask about sofas, fabrics, sizing, styling or care…")
if st.session_state.get("pending_prompt"):
    user_input = st.session_state.pop("pending_prompt") or user_input

if user_input:
    # Show the visitor's message immediately.
    with st.chat_message("user", avatar="🙂"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🛋️"):
        try:
            with st.spinner(f"{ASSISTANT_NAME} is thinking…"):
                reply = bot.chat(user_input, context=visitor_context)
            st.markdown(reply)
        except GeminiError as error:
            # Graceful failure: explain the problem, keep the conversation intact.
            st.error(error.message)
            if error.hint:
                st.caption(error.hint)

_powered_by = (
    f"✨ Powered by Google Gemini · <b>{MODEL_NAME}</b>"
    if not st.session_state.demo_mode
    else "Demo mode — add a Gemini API key in Secrets for live AI answers"
)
st.markdown(
    f"""
    <div class="mg-footer">
      Maison &amp; Grain · Furniture &amp; interiors guidance · Prices shown are
      indicative and should be confirmed with the showroom.<br/>{_powered_by}
    </div>
    """,
    unsafe_allow_html=True,
)
if st.session_state.demo_mode:
    st.caption("ℹ️ Demo mode is on — replies are sample answers, not live Gemini responses.")

with st.expander("📊 Session statistics"):
    st.caption(bot.report())
