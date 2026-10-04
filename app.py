import os
import asyncio

import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
from telegram import Bot

from prompts import (
    ANALYZE_IMAGE_PROMPT,
    READ_TEXT_PROMPT,
    EXPLAIN_TEXT_PROMPT,
    ACCESSIBILITY_PROMPT,
    CHAT_SYSTEM_PROMPT,
    WELCOME_MESSAGE,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="VisionMate AI",
    page_icon="👁️",
    layout="centered",
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# LOAD SECRETS
# ============================================================

def get_secret(name):
    """
    Read secrets from Streamlit Cloud when deployed.
    Read .env when running locally.
    """

    try:
        return st.secrets.get(
            name,
            os.getenv(name, "")
        )
    except Exception:
        return os.getenv(name, "")


GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = get_secret("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = get_secret("TELEGRAM_CHAT_ID")


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

MODEL_NAME = "gemini-3.8-flash"


@st.cache_resource
def get_gemini_client():

    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


# ============================================================
# TELEGRAM
# ============================================================

def send_telegram(message):

    if not TELEGRAM_BOT_TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN is not configured."
        )

    if not TELEGRAM_CHAT_ID:
        raise ValueError(
            "TELEGRAM_CHAT_ID is not configured."
        )

    async def send_message():

        bot = Bot(
            token=TELEGRAM_BOT_TOKEN
        )

        async with bot:

            await bot.send_message(
                chat_id=str(TELEGRAM_CHAT_ID),
                text=message
            )

    asyncio.run(send_message())


# ============================================================
# IMAGE ANALYSIS
# ============================================================

def analyze_image(
    image_bytes,
    mime_type,
    prompt
):

    client = get_gemini_client()

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            prompt,
            image_part
        ]
    )

    return response.text


# ============================================================
# FOLLOW-UP QUESTION
# ============================================================

def ask_followup(
    image_bytes,
    mime_type,
    question
):

    client = get_gemini_client()

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )

    prompt = f"""
{CHAT_SYSTEM_PROMPT}

User question:

{question}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            prompt,
            image_part
        ]
    )

    return response.text


# ============================================================
# HEADER
# ============================================================

st.title("👁️ VisionMate AI")

st.markdown(
    """
### See the world differently

Upload an image and let **VisionMate AI** understand it.

**Read text • Understand scenes • Study • Ask questions**
"""
)

st.info(
    """
VisionMate AI is an AI-powered visual assistant that helps
users understand images, read text, explain study material,
and get accessible descriptions of visual scenes.
"""
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("👁️ VisionMate AI")

    st.write(
        """
VisionMate AI helps users understand visual information
using artificial intelligence.

### Features

📷 Analyze images

📖 Read text

🧠 Explain study material

♿ Accessibility descriptions

💬 Ask follow-up questions

📨 Send summaries to Telegram
"""
    )

    st.divider()

    st.subheader("About")

    st.write(
        """
VisionMate AI was built as a hands-on AI project using
Python, Streamlit, Google Gemini, and Telegram.
"""
    )


# ============================================================
# IMAGE UPLOAD
# ============================================================

st.subheader("📷 Upload an Image")

uploaded_file = st.file_uploader(
    "Choose an image",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp"
    ]
)


# ============================================================
# SESSION STATE
# ============================================================

if "ai_response" not in st.session_state:

    st.session_state.ai_response = ""


if "image_bytes" not in st.session_state:

    st.session_state.image_bytes = None


if "mime_type" not in st.session_state:

    st.session_state.mime_type = None


# ============================================================
# IMAGE PROCESSING
# ============================================================

if uploaded_file is not None:

    image_bytes = uploaded_file.getvalue()

    mime_type = uploaded_file.type

    st.session_state.image_bytes = image_bytes

    st.session_state.mime_type = mime_type


    # --------------------------------------------------------
    # DISPLAY IMAGE
    # --------------------------------------------------------

    st.image(
        image_bytes,
        caption="Uploaded Image",
        use_container_width=True
    )


    st.divider()

    st.subheader("🔍 Choose an Action")


    # --------------------------------------------------------
    # ACTION BUTTONS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        analyze_button = st.button(
            "🔍 Analyze Image",
            use_container_width=True
        )

        read_button = st.button(
            "📖 Read Text",
            use_container_width=True
        )


    with col2:

        explain_button = st.button(
            "🧠 Explain This Text",
            use_container_width=True
        )

        accessibility_button = st.button(
            "♿ Accessibility Mode",
            use_container_width=True
        )


    # ========================================================
    # ANALYZE IMAGE
    # ========================================================

    if analyze_button:

        with st.spinner(
            "🔍 Analyzing the image..."
        ):

            try:

                result = analyze_image(
                    image_bytes,
                    mime_type,
                    ANALYZE_IMAGE_PROMPT
                )

                st.session_state.ai_response = result

            except Exception as e:

                error = str(e)

                if (
                    "429" in error
                    or "RESOURCE_EXHAUSTED" in error
                ):

                    st.error(
                        """
⚠️ Gemini API rate limit reached.

Please wait a little and try again.
"""
                    )

                else:

                    st.error(
                        f"❌ Error:\n\n{error}"
                    )


    # ========================================================
    # READ TEXT
    # ========================================================

    if read_button:

        with st.spinner(
            "📖 Reading text..."
        ):

            try:

                result = analyze_image(
                    image_bytes,
                    mime_type,
                    READ_TEXT_PROMPT
                )

                st.session_state.ai_response = result

            except Exception as e:

                error = str(e)

                if (
                    "429" in error
                    or "RESOURCE_EXHAUSTED" in error
                ):

                    st.error(
                        """
⚠️ Gemini API rate limit reached.

Please wait a little and try again.
"""
                    )

                else:

                    st.error(
                        f"❌ Error:\n\n{error}"
                    )


    # ========================================================
    # EXPLAIN TEXT
    # ========================================================

    if explain_button:

        with st.spinner(
            "🧠 Explaining the content..."
        ):

            try:

                result = analyze_image(
                    image_bytes,
                    mime_type,
                    EXPLAIN_TEXT_PROMPT
                )

                st.session_state.ai_response = result

            except Exception as e:

                error = str(e)

                if (
                    "429" in error
                    or "RESOURCE_EXHAUSTED" in error
                ):

                    st.error(
                        """
⚠️ Gemini API rate limit reached.

Please wait a little and try again.
"""
                    )

                else:

                    st.error(
                        f"❌ Error:\n\n{error}"
                    )


    # ========================================================
    # ACCESSIBILITY MODE
    # ========================================================

    if accessibility_button:

        with st.spinner(
            "♿ Creating accessibility description..."
        ):

            try:

                result = analyze_image(
                    image_bytes,
                    mime_type,
                    ACCESSIBILITY_PROMPT
                )

                st.session_state.ai_response = result

            except Exception as e:

                error = str(e)

                if (
                    "429" in error
                    or "RESOURCE_EXHAUSTED" in error
                ):

                    st.error(
                        """
⚠️ Gemini API rate limit reached.

Please wait a little and try again.
"""
                    )

                else:

                    st.error(
                        f"❌ Error:\n\n{error}"
                    )


# ============================================================
# AI RESPONSE
# ============================================================

if st.session_state.ai_response:

    st.divider()

    st.subheader(
        "🤖 VisionMate AI Response"
    )

    st.markdown(
        st.session_state.ai_response
    )


    # ========================================================
    # TELEGRAM ACTION
    # ========================================================

    st.divider()

    st.subheader("📨 Send Summary")

    st.write(
        """
Send the AI-generated response directly
to your VisionMate AI Telegram bot.
"""
    )


    telegram_button = st.button(
        "📨 Send Summary to Telegram",
        use_container_width=True
    )


    if telegram_button:

        telegram_message = (
            "👁️ VisionMate AI Summary\n\n"
            + st.session_state.ai_response
        )

        try:

            with st.spinner(
                "📨 Sending to Telegram..."
            ):

                send_telegram(
                    telegram_message
                )

            st.success(
                "✅ Summary successfully sent to Telegram!"
            )

        except Exception as e:

            st.error(
                f"❌ Telegram error:\n\n{str(e)}"
            )


# ============================================================
# FOLLOW-UP CHAT
# ============================================================

if st.session_state.image_bytes is not None:

    st.divider()

    st.subheader(
        "💬 Ask VisionMate"
    )

    st.write(
        "Ask a follow-up question about the uploaded image."
    )


    question = st.text_input(
        "Your question",
        placeholder=(
            "Example: What is the main idea of this image?"
        )
    )


    ask_button = st.button(
        "💬 Ask VisionMate",
        use_container_width=True
    )


    if ask_button:

        if not question.strip():

            st.warning(
                "Please enter a question first."
            )

        else:

            with st.spinner(
                "💬 Thinking..."
            ):

                try:

                    answer = ask_followup(
                        st.session_state.image_bytes,
                        st.session_state.mime_type,
                        question
                    )

                    st.subheader(
                        "🤖 Answer"
                    )

                    st.markdown(
                        answer
                    )

                except Exception as e:

                    error = str(e)

                    if (
                        "429" in error
                        or "RESOURCE_EXHAUSTED" in error
                    ):

                        st.error(
                            """
⚠️ Gemini API rate limit reached.

Please wait a little and try again.
"""
                        )

                    else:

                        st.error(
                            f"❌ Error:\n\n{error}"
                        )


# ============================================================
# WELCOME MESSAGE
# ============================================================

if uploaded_file is None:

    st.markdown(
        WELCOME_MESSAGE
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "👁️ VisionMate AI • AI-powered visual assistant"
)