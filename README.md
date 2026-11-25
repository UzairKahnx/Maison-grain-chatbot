# 🛋️ Maison & Grain — Furniture Showroom Chatbot

A domain-focused conversational assistant for a premium furniture showroom, built with
**Streamlit** and the **Google Gemini API** (key from Google AI Studio). The assistant
stays strictly inside the furniture/interiors domain and politely redirects off-topic
questions. Its behaviour is defined mainly by a carefully designed system prompt.

### 🚀 Live demo
**https://maison-grain-chatbot-ynfigfasfemhxe2ftneffv.streamlit.app/**

*Source code: https://github.com/UzairKahnx/Maison-grain-chatbot*

---

## 1. Assignment requirements → implementation

| Requirement | Where it is implemented |
|---|---|
| Single domain focus + off-topic redirect | `src/prompt.py` → `SYSTEM_PROMPT` (Role, Context, Constraints, Few-shot examples) |
| System prompt design | `src/prompt.py` — role, audience, scope, constraints, catalogue knowledge |
| Model configuration + justification | `src/prompt.py` constants and the table in section 3 below |
| LLM API | Google Gemini REST API (`gemini-3.5-flash-lite`) in `src/gemini_client.py` |
| Working code, graceful failures, conversation history | `chatbot.py` memory class + Streamlit `session_state`; `GeminiError`, retries, timeouts, friendly fallbacks |
| Deployment with public link | Streamlit Community Cloud — steps in section 6 |
| Attractive UI/UX & graphics | `src/ui.py` — custom CSS theme, inline SVG artwork, responsive cards |

---

## 2. System prompt design

The prompt has five deliberate layers:

1. **Role** — "Maya", a senior interior design consultant at Maison & Grain, with 12
   years of experience. Tone: warm, confident, sophisticated, never salesy. This gives
   the model a consistent persona instead of a generic assistant voice.
2. **Context** — the audience (homeowners, renters, first-time buyers, design fans),
   the scope (furniture, materials, sizing, styling, care, delivery, warranty) and
   explicit constraints (stay in domain, no licensed advice, never invent facts,
   indicative prices only, short skimmable answers, at most one clarifying question).
3. **Background knowledge** — a compact in-prompt catalogue of six pieces with sizes,
   materials and indicative starting prices, plus care instructions and services. This
   grounds answers in real showroom data without needing a vector database.
4. **Response rules** — recommend at most two products, use the 90 cm walkway rule for
   sizing, and use a fixed, polite redirection pattern for off-topic questions.
5. **Few-shot examples** — three short ideal exchanges (sofa advice, off-topic sport
   question, fabric care) that demonstrate tone, length and the domain guardrail.

The full prompt is in `src/prompt.py` and can be viewed inside the app under
**"About Maya & model settings"** in the sidebar.

---

## 3. Model configuration and justification

| Parameter | Value | Why |
|---|---|---|
| Model | `gemini-3.5-flash-lite` | Current stable, fast and cost-efficient — ideal for a responsive chat UI. `gemini-2.0-flash` has been shut down by Google. Override any time with the `GEMINI_MODEL` secret (e.g. `gemini-3.8-flash`). |
| Temperature | `0.6` | A middle setting: low enough to keep catalogue facts (sizes, prices, materials) accurate and consistent, high enough for warm, natural, non-robotic phrasing. |
| Max output tokens | `600` | Chat answers should be scannable. This caps replies at roughly 3–6 short paragraphs, preventing rambling while leaving room for two product recommendations. |
| Top-p | `0.9` | Mild nucleus sampling filters out unlikely word choices, complementing temperature for polished, professional wording. |
| History window | last 12 messages (6 turns) | Keeps context across turns while controlling latency and token cost. |

These values are passed directly in the `generationConfig` of every API request.

---

## 4. Features

- **Domain guardrail** — off-topic questions are politely declined and redirected in
  one short reply, enforced by the system prompt and its few-shot examples.
- **Persistent conversation history** — stored in `st.session_state`; only recent turns
  are sent to Gemini, so the assistant remembers earlier context.
- **Graceful error handling** — invalid keys (401/403), rate limits (429 with two
  retries and backoff), server errors (5xx), timeouts, network failures, safety blocks
  and malformed responses all become friendly, actionable messages. The conversation
  is preserved so the visitor can simply retry.
- **API key required** — there is no offline/demo fallback. Without a Gemini key the app
  shows a setup screen and refuses to chat, so every conversation genuinely uses the API.
- **Notebook-style engine** — `chatbot.py` follows the class lab: secure key loading,
  token counting, history truncation, guardrails, streaming and JSON output, plus an
  interactive CLI. The Streamlit app uses this same engine.
- **Visitor preferences** — room, style and budget selectors in the sidebar are passed
  as lightweight context with each message, personalising recommendations.
- **Attractive, responsive UI** — warm showroom palette, editorial hero, trust bar,
  collection cards, suggestion chips, custom chat bubbles and mobile-friendly layout.
  All graphics are local inline SVG, so there are no broken image links.

---

## 5. Run locally

### Prerequisites
- Python 3.9+ and pip

### Steps
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. REQUIRED: add your key for local use — do NOT commit this file
mkdir .streamlit
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
# edit .streamlit/secrets.toml and paste your key

# 3. Start the app
streamlit run app.py
```

Open the URL shown in the terminal (normally `http://localhost:8501`).

### Getting a Gemini API key
1. Go to **Google AI Studio** → <https://aistudio.google.com/apikey>
2. Sign in with a Google account and click **Create API key**.
3. Copy the key (starts with `AIza…`) into `.streamlit/secrets.toml` as shown above,
   or paste it into the sidebar field for a quick local test.

A key is **mandatory**. If none is found, the app displays a setup screen with
instructions and disables the chat — it will never answer with sample/offline replies.

### Try these prompts
- "Help me choose a sofa for a small living room"
- "How do I care for cream bouclé?"
- "What size dining table do I need for 6 people?"
- "Who won the football final?" → tests the domain guardrail

### CLI chatbot and Colab notebook
```bash
python chatbot.py                  # interactive terminal chat (requires a key)
python chatbot.py --stream         # same, with streamed replies
```
`chatbot.py` mirrors the lab notebook sections (memory class, token stats, guardrails,
streaming, structured JSON output and an interactive loop). A ready-to-run Colab version
adapted to Gemini is in `notebookfile/furniture_chatbot.ipynb`.

---

## 6. Deploy to Streamlit Community Cloud (public link)

1. **Create a GitHub repository** and push this folder:
   ```bash
   git init
   git add .
   git commit -m "Furniture showroom chatbot"
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```
   Make sure `.streamlit/secrets.toml` is **not** committed (it is in `.gitignore`).
   Commit `.streamlit/secrets.toml.example` instead.

2. **Sign in** to <https://share.streamlit.io> with GitHub.

3. Click **New app** and set:
   - Repository: `<your-username>/<your-repo>`
   - Branch: `main`
   - Main file path: `app.py`

4. Open **Advanced settings → Secrets** and paste:
   ```toml
   GEMINI_API_KEY = "your-real-key-from-google-ai-studio"
   ```
   (Alternatively set an environment variable `GEMINI_API_KEY` in the same panel.)

5. Click **Deploy**. Streamlit builds the app and gives you a public URL like
   `https://<your-repo>-<hash>.streamlit.app` that anyone can open. For this project the
   deployed link is
   **https://maison-grain-chatbot-ynfigfasfemhxe2ftneffv.streamlit.app/**.

6. To update the app later, just push to GitHub — the app redeploys automatically.

> **Security tip:** never paste your API key into chat, code or screenshots. Rotate it
> in Google AI Studio immediately if it is ever exposed. Free-tier keys have per-minute
> and per-day quotas; for heavy traffic, use a paid tier or restrict the key.

### Keeping your key private on a public app
- The key is read **only on the server** from `st.secrets` (Streamlit Cloud Secrets) or
  an environment variable. It is never sent to the browser, never stored in
  `session_state`, and never written to a file that gets committed.
- `.streamlit/secrets.toml` is in `.gitignore`. Only `secrets.toml.example` is committed.
- **Optional invite-only gate:** add a second secret in Streamlit Cloud:
  ```toml
  APP_ACCESS_CODE = "choose-a-private-code"
  ```
  Visitors then see a lock screen and must enter that code before the chat loads. This
  stops strangers from consuming your API quota through the public link. Share the code
  only with people you want to test the bot. Use **🔒 Lock this conversation** in the
  sidebar to sign out. If `APP_ACCESS_CODE` is not set, the app is open to everyone.
- If a key is ever exposed anywhere (including a chat message), **delete it in Google AI
  Studio**, create a new one, and update only the Streamlit Cloud Secret — no code change
  or redeploy of the repository is needed.

---

## 7. Project structure

```
.
├── app.py                       # Streamlit UI, chat loop, session state
├── chatbot.py                   # notebook-style engine + interactive CLI
├── requirements.txt             # streamlit, requests, Pillow
├── README.md                    # this guide
├── .gitignore                   # protects secrets
├── notebookfile/
│   ├── Conversational_chatbots_PSEB.ipynb  # original class lab (reference)
│   └── furniture_chatbot.ipynb             # Colab lab adapted to Gemini + furniture domain
├── .streamlit/
│   ├── config.toml              # theme (showroom colours)
│   └── secrets.toml.example     # template for your API key
├── assets/
│   ├── hero.svg                 # showroom hero illustration
│   ├── sofa.svg                 # product illustrations
│   ├── chair.svg
│   └── table.svg
└── src/
    ├── __init__.py
    ├── prompt.py                # system prompt + model configuration
    ├── gemini_client.py         # Gemini REST client, retries, error translation
    └── ui.py                    # CSS, SVG rendering, UI components
```

---

## 8. Design notes

The assistant demonstrates that most of a specialised chatbot's behaviour can come from
prompt engineering: the persona, domain boundary, product knowledge, response format and
guardrails are all natural-language instructions in `SYSTEM_PROMPT`. The application code
only handles transport, state and presentation — it contains no domain rules of its own.
Every reply comes from the Gemini API; the app cannot answer without a key.
