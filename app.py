import json
import urllib.request
import urllib.parse
import streamlit as st
from google import genai
from google.genai import types

from prompts import (
    SUMMARY_REQUEST_PROMPT,
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
)

# Page configuration
st.set_page_config(
    page_title="Snap & Study — AI Concept Tutor",
    page_icon="🎓",
    layout="centered",
)

MODEL_NAME = "gemini-2.5-flash"

# Validate and load secrets
if "GEMINI_API_KEY" not in st.secrets or "TELEGRAM_BOT_TOKEN" not in st.secrets:
    st.error(
        "⚠️ Missing secrets! Please ensure `GEMINI_API_KEY` and `TELEGRAM_BOT_TOKEN` "
        "are configured in `.streamlit/secrets.toml`."
    )
    st.stop()

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]


@st.cache_resource
def get_gemini_client():
    """Build the Gemini client once and cache it to avoid reconnection churn across reruns."""
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


def send_telegram(chat_id: str, text: str):
    """
    Sends study summary notes to the student's Telegram chat using Telegram Bot API.
    Truncates or splits if exceeding Telegram's 4096-character limit.
    """
    if not text:
        return False, "No summary text generated."

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    # Telegram max limit is 4096 characters per message
    clean_text = text if len(text) <= 4000 else text[:3996] + "..."

    payload = json.dumps({
        "chat_id": chat_id.strip(),
        "text": clean_text,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
            if result.get("ok"):
                return True, "Delivered"
            return False, result.get("description", "Failed to deliver message.")
    except urllib.error.HTTPError as http_err:
        try:
            err_details = json.loads(http_err.read().decode())
            return False, err_details.get("description", str(http_err))
        except Exception:
            return False, str(http_err)
    except Exception as err:
        return False, str(err)


def render_message(message):
    """Renders a text or image message within the Streamlit chat UI."""
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])


def add_message(role, kind, content):
    """Adds a message to history in session_state and immediately renders it."""
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])


def ask_gemini(parts):
    """Sends prompt parts (text and/or image) to the ongoing Gemini chat session."""
    try:
        response = st.session_state.chat.send_message(parts)
        return response.text
    except Exception as error:
        return f"Sorry, I ran into an error while processing that: {error}"


# ==========================================
# Step 1: Onboarding Screen
# ==========================================
if "onboarded" not in st.session_state:
    st.title("🎓 Snap & Study")
    st.caption("Snap a problem. Master the concept. Receive revision notes on Telegram.")

    with st.form("onboarding_form"):
        name = st.text_input("Your Name", placeholder="e.g. Pooja")
        telegram_chat_id = st.text_input(
            "Telegram Chat ID",
            placeholder="e.g. 123456789",
            help="Send /start to your bot, or check @userinfobot on Telegram to get your numeric ID.",
        )
        submitted = st.form_submit_button("Start Learning 🚀")

    if submitted:
        if not name.strip() or not telegram_chat_id.strip():
            st.warning("Please fill in both your name and your Telegram Chat ID.")
        else:
            st.session_state.name = name.strip()
            st.session_state.telegram_chat_id = telegram_chat_id.strip()
            # Initialize Gemini chat with system prompt
            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            )
            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()

    st.stop()


# ==========================================
# Step 2: Main Study Chat Interface
# ==========================================
header_col, button_col = st.columns([5, 3], vertical_alignment="center")

with header_col:
    st.title("🎓 Snap & Study")

with button_col:
    send_disabled = len(st.session_state.messages) <= 2
    if st.button("📤 Send Notes to Telegram", disabled=send_disabled, use_container_width=True):
        with st.spinner("Generating concise study notes & dispatching to Telegram..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
            success, info = send_telegram(st.session_state.telegram_chat_id, summary)

        if success:
            st.success("Study notes sent! Check your Telegram 📲")
        else:
            st.error(f"Couldn't send to Telegram: {info}")

st.caption(
    f"Logged in as **{st.session_state.name}** · Notes destination: Telegram ID `{st.session_state.telegram_chat_id}`"
)

# Display chat history or welcome message
if not st.session_state.messages:
    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name),
    )
else:
    for message in st.session_state.messages:
        render_message(message)

# ==========================================
# Step 3: Handling Input (Text & Photos)
# ==========================================
user_input = st.chat_input(
    "Ask a study question, or attach a photo of a problem / diagram...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append("Please explain the concept, problem, or diagram in this photo step-by-step.")

    with st.spinner("Analyzing and breaking down the concept..."):
        answer = ask_gemini(parts)
        add_message("assistant", "text", answer)
