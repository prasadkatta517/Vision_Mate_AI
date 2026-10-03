import os
import streamlit as st
import google.genai as genai
from google.genai import types

from prompts import (
    ANALYZE_IMAGE_PROMPT,
    READ_TEXT_PROMPT,
    EXPLAIN_TEXT_PROMPT,
    ACCESSIBILITY_PROMPT,
    CHAT_SYSTEM_PROMPT,
    WELCOME_MESSAGE,
)


# Page Configuration

st.set_page_config(
    page_title="VisionMate AI",
    page_icon="👁️",
    layout="centered",
)

# API Key

API_KEY = None

# Streamlit Cloud Secrets
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# Local .env fallback
if not API_KEY:
    try:
        from dotenv import load_dotenv

        load_dotenv()
        API_KEY = os.getenv("GEMINI_API_KEY")
    except Exception:
        pass

if not API_KEY:
    st.error(
        "GEMINI_API_KEY was not found. "
        "Please add it to Streamlit Secrets or your local .env file."
    )
    st.stop()

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.8-flash"


# Session State

if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None

if "image_type" not in st.session_state:
    st.session_state.image_type = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ============================================================
# Custom CSS
# ============================================================

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 25px;
    }

    .tool-card {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 15px;
    }

    .tool-title {
        font-size: 20px;
        font-weight: 600;
    }

    .tool-description {
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Header
# ============================================================

st.markdown(
    '<div class="main-title">👁️ VisionMate AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Your Real-World Visual Assistant</div>',
    unsafe_allow_html=True,
)

# ============================================================
# Hero Section
# ============================================================

st.info(
    """
### 👁️ See the world differently

Upload an image and let VisionMate AI understand it.

**Read text • Understand scenes • Study • Ask questions**
"""
)

# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.header("👁️ VisionMate AI")

    st.write(
        """
        VisionMate AI is an AI-powered visual assistant
        that helps users understand images, read text,
        explain study material, and ask questions about images.
        """
    )

    st.divider()

    st.subheader("Available Tools")

    st.write("🔍 Analyze Image")
    st.write("📖 Read Text")
    st.write("🧠 Explain This Text")
    st.write("♿ Accessibility Mode")
    st.write("💬 Ask VisionMate")

# ============================================================
# Image Upload
# ============================================================

st.subheader("📷 Upload an Image")

uploaded_file = st.file_uploader(
    "Choose an image",
    type=["jpg", "jpeg", "png"],
)

if uploaded_file is not None:

    st.session_state.image_bytes = uploaded_file.getvalue()
    st.session_state.image_type = uploaded_file.type

    st.image(
        st.session_state.image_bytes,
        caption="Uploaded Image",
        use_container_width=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Remove Image", use_container_width=True):
            st.session_state.image_bytes = None
            st.session_state.image_type = None
            st.session_state.messages = []
            st.rerun()

    with col2:
        if st.button("🔄 Reset Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# ============================================================
# Tool Cards
# ============================================================

st.subheader("🛠️ VisionMate Tools")

col1, col2 = st.columns(2)

with col1:

    st.markdown(
        """
        <div class="tool-card">
        <div class="tool-title">🔍 Analyze Image</div>
        <div class="tool-description">
        Understand objects, people, surroundings and
        important visual details.
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="tool-card">
        <div class="tool-title">🧠 Explain This Text</div>
        <div class="tool-description">
        Turn study material into simple explanations,
        key points and exam questions.
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:

    st.markdown(
        """
        <div class="tool-card">
        <div class="tool-title">📖 Read Text</div>
        <div class="tool-description">
        Extract readable text from images.
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="tool-card">
        <div class="tool-title">♿ Accessibility Mode</div>
        <div class="tool-description">
        Get a detailed description of visual scenes.
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# Image Analysis Functions
# ============================================================

def generate_image_response(prompt):
    image_part = types.Part.from_bytes(
        data=st.session_state.image_bytes,
        mime_type=st.session_state.image_type,
    )

    return client.models.generate_content(
        model=MODEL_NAME,
        contents=[image_part, prompt],
    )


# ============================================================
# Action Buttons
# ============================================================

st.subheader("⚡ Choose an Action")

col1, col2 = st.columns(2)

with col1:

    analyze_button = st.button(
        "🔍 Analyze Image",
        use_container_width=True,
    )

    read_button = st.button(
        "📖 Read Text",
        use_container_width=True,
    )

with col2:

    explain_button = st.button(
        "🧠 Explain This Text",
        use_container_width=True,
    )

    accessibility_button = st.button(
        "♿ Accessibility Mode",
        use_container_width=True,
    )

# ============================================================
# Button Processing
# ============================================================

if any(
    [
        analyze_button,
        read_button,
        explain_button,
        accessibility_button,
    ]
):

    if st.session_state.image_bytes is None:

        st.warning("Please upload an image first.")

    else:

        try:

            if analyze_button:

                with st.spinner("Analyzing image..."):

                    response = generate_image_response(
                        ANALYZE_IMAGE_PROMPT
                    )

                st.subheader("🔍 Image Analysis")
                st.write(response.text)

            elif read_button:

                with st.spinner("Reading text..."):

                    response = generate_image_response(
                        READ_TEXT_PROMPT
                    )

                st.subheader("📖 Extracted Text")
                st.write(response.text)

            elif explain_button:

                with st.spinner("Explaining the content..."):

                    response = generate_image_response(
                        EXPLAIN_TEXT_PROMPT
                    )

                st.subheader("🧠 Explanation")
                st.write(response.text)

            elif accessibility_button:

                with st.spinner("Creating accessibility description..."):

                    response = generate_image_response(
                        ACCESSIBILITY_PROMPT
                    )

                st.subheader("♿ Accessibility Description")
                st.write(response.text)

        except Exception as e:

            error_message = str(e)

            if "429" in error_message:

                st.warning(
                    "⚠️ Gemini API request limit reached. "
                    "Please wait for the quota to reset and try again later."
                )

            else:

                st.error(
                    "Something went wrong while processing the image."
                )

# ============================================================
# Follow-up Chat
# ============================================================

st.divider()

st.subheader("💬 Ask VisionMate")

if st.session_state.image_bytes is None:

    st.info("Upload an image first to ask questions about it.")

else:

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_question = st.chat_input(
        "Ask a question about the image..."
    )

    if user_question:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_question,
            }
        )

        with st.chat_message("user"):
            st.write(user_question)

        try:

            with st.chat_message("assistant"):

                with st.spinner("Thinking..."):

                    image_part = types.Part.from_bytes(
                        data=st.session_state.image_bytes,
                        mime_type=st.session_state.image_type,
                    )

                    contents = [
                        CHAT_SYSTEM_PROMPT,
                        image_part,
                    ]

                    for message in st.session_state.messages:
                        contents.append(
                            f'{message["role"]}: {message["content"]}'
                        )

                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=contents,
                    )

                    answer = response.text

                    st.write(answer)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

        except Exception as e:

            error_message = str(e)

            if "429" in error_message:

                st.warning(
                    "⚠️ Gemini API request limit reached. "
                    "Please wait for the quota to reset."
                )

            else:

                st.error(
                    "Something went wrong while answering your question."
                )

# ============================================================
# About
# ============================================================

st.divider()

st.subheader("ℹ️ About VisionMate AI")

st.write(
    """
    VisionMate AI is an AI-powered visual assistant built
    using Python, Streamlit and Google Gemini.

    It can analyze images, extract text, explain study material,
    provide accessibility descriptions and answer questions
    about uploaded images.
    """
)