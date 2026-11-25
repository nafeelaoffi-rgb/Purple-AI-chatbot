import streamlit as st
import pandas as pd
import nltk
import wikipedia
from difflib import SequenceMatcher
from ddgs import DDGS


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Purple AI Assistant",
    page_icon="💜",
    layout="centered"
)


# ============================================================
# LOAD CSV
# ============================================================

data = pd.read_csv("responses.csv").fillna("")


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "tanglish_mode" not in st.session_state:
    st.session_state.tanglish_mode = False


# ============================================================
# CLEAN TEXT
# ============================================================

def clean(text):

    words = nltk.wordpunct_tokenize(
        str(text).lower()
    )

    return " ".join(
        word for word in words
        if word.isalpha()
    )


# ============================================================
# CSV SEARCH
# ============================================================

def csv_search(question):

    best_score = 0
    answer = None

    for _, row in data.iterrows():

        score = SequenceMatcher(
            None,
            clean(question),
            clean(row["Question"])
        ).ratio()

        if score > best_score:

            best_score = score
            answer = row["Response"]

    if best_score >= 0.80:
        return answer

    return None


# ============================================================
# WIKIPEDIA SEARCH
# ============================================================

def wiki_search(question):

    try:

        topic = question.lower()

        for word in [
            "what is",
            "who is",
            "explain"
        ]:

            topic = topic.replace(
                word,
                ""
            )

        topic = topic.strip(" ?")

        if not topic:
            return None

        results = wikipedia.search(
            topic,
            results=1
        )

        if results:

            summary = wikipedia.summary(
                results[0],
                sentences=4,
                auto_suggest=False
            )

            lines = summary.split(". ")

            answer = (
                f"### 😊 {results[0]}\n\n"
            )

            answer += (
                " ".join(lines[:2])
                + "\n\n"
            )

            answer += (
                "**💕 Key Points:**\n\n"
            )

            for line in lines[2:4]:

                answer += (
                    f"- **{line.strip().rstrip('.')}**\n"
                )

            return answer

    except Exception:

        return None

    return None


# ============================================================
# WEB SEARCH
# ============================================================

def web_search(question):

    try:

        results = DDGS().text(
            question,
            max_results=1
        )

        if results:

            result = results[0]

            body = result.get(
                "body",
                ""
            )

            href = result.get(
                "href",
                ""
            )

            if body:

                return (
                    body
                    + "\n\nSource: "
                    + href
                )

    except Exception:

        pass

    return "Sorry! I couldn't find an answer."


# ============================================================
# MAIN CHATBOT
# ============================================================

def chatbot(question):

    current_words = [
        "current",
        "latest",
        "today",
        "ranking",
        "rankings",
        "news",
        "no.1",
        "number one"
    ]

    # Current information
    if any(
        word in question.lower()
        for word in current_words
    ):

        return web_search(question)

    # CSV
    answer = csv_search(question)

    if answer:
        return answer

    # Wikipedia
    answer = wiki_search(question)

    if answer:
        return answer

    # Web search
    return web_search(question)


# ============================================================
# PURPLE AI DESIGN
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       FULL PURPLE BACKGROUND
       -------------------------------------------------------- */

    .stApp {

        background:
            linear-gradient(
                135deg,
                #F3E8FF 0%,
                #EDE9FE 50%,
                #F5F3FF 100%
            );

        min-height: 100vh;
    }


    /* --------------------------------------------------------
       FALLING SNOW
       -------------------------------------------------------- */

    .stApp::before {

        content: "❄  ·  ❄  ·  ❄  ·  ❄  ·  ❄  ·  ❄";

        position: fixed;

        top: -50px;
        left: 0;

        width: 100%;

        height: 110vh;

        color: rgba(
            255,
            255,
            255,
            0.75
        );

        font-size: 22px;

        word-spacing: 35px;

        line-height: 100px;

        white-space: pre-wrap;

        pointer-events: none;

        z-index: 0;

        animation:
            snowFall 10s linear infinite;
    }


    @keyframes snowFall {

        from {

            transform:
                translateY(-100px);
        }

        to {

            transform:
                translateY(100vh);
        }
    }


    /* --------------------------------------------------------
       KEEP CONTENT ABOVE SNOW
       -------------------------------------------------------- */

    .main {

        position: relative;

        z-index: 1;
    }


    /* --------------------------------------------------------
       MAIN TITLE
       -------------------------------------------------------- */

    h1 {

        color: #6B21A8 !important;

        text-align: center;

        font-weight: 800;

        letter-spacing: 1px;

        text-shadow:
            0 0 15px
            rgba(
                147,
                51,
                234,
                0.30
            );
    }


    /* --------------------------------------------------------
       WELCOME TITLE
       -------------------------------------------------------- */

    h2 {

        color: #581C87 !important;

        text-align: center;

        font-weight: 800;
    }


    /* --------------------------------------------------------
       CAPTION
       -------------------------------------------------------- */

    .stCaption {

        text-align: center;

        color: #7E22CE !important;

        font-size: 17px;
    }


    /* --------------------------------------------------------
       CHAT MESSAGES
       -------------------------------------------------------- */

    div[data-testid="stChatMessage"] {

        border-radius: 24px;

        padding: 16px;

        max-width: 75%;

        backdrop-filter: blur(10px);

        transition: 0.3s;
    }


    div[data-testid="stChatMessage"]:hover {

        transform: translateY(-2px);
    }


    /* --------------------------------------------------------
       USER MESSAGE
       -------------------------------------------------------- */

    div[data-testid="stChatMessage"]:has(
        div[data-testid="stChatMessageAvatarUser"]
    ) {

        background:
            linear-gradient(
                135deg,
                #9333EA,
                #6D28D9
            );

        color: white;

        margin-left: auto;

        margin-right: 0;

        flex-direction: row-reverse;

        box-shadow:
            0 6px 20px
            rgba(
                126,
                34,
                206,
                0.25
            );
    }


    /* --------------------------------------------------------
       AI MESSAGE
       -------------------------------------------------------- */

    div[data-testid="stChatMessage"]:has(
        div[data-testid="stChatMessageAvatarAssistant"]
    ) {

        background:
            rgba(
                255,
                255,
                255,
                0.85
            );

        color: #581C87;

        margin-left: 0;

        margin-right: auto;

        border:
            1px solid #DDD6FE;

        box-shadow:
            0 5px 20px
            rgba(
                126,
                34,
                206,
                0.10
            );
    }


    div[data-testid="stChatMessage"] * {

        color: inherit;
    }


    /* --------------------------------------------------------
       CHAT INPUT
       -------------------------------------------------------- */

    div[data-testid="stChatInput"] {

        border-radius: 25px;
    }


    /* --------------------------------------------------------
       BUTTONS
       -------------------------------------------------------- */

    .stButton > button {

        border-radius: 20px;

        border:
            1px solid #D8B4FE;

        background:
            rgba(
                255,
                255,
                255,
                0.85
            );

        color: #6B21A8;

        font-weight: 600;

        transition: 0.3s;
    }


    .stButton > button:hover {

        background: #E9D5FF;

        border-color: #A855F7;

        transform: translateY(-2px);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# MAIN TITLE
# ============================================================

st.title("✨ Purple AI Assistant")


# ============================================================
# WELCOME SCREEN
# ============================================================

if len(st.session_state.messages) == 0:

    # Space before welcome message
    st.write("")

    st.write("")

    # Welcome message
    st.subheader(
        "Welcome, Google Refuser 😁"
    )

    st.caption(
        "Your personal Purple AI is ready to think, search & chat 💜"
    )

    st.write("")

    st.markdown(
        "### ✨ Try asking me"
    )

    # --------------------------------------------------------
    # QUICK BUTTONS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "📚 Explain Python",
            use_container_width=True
        ):

            question = "Explain Python"

            st.session_state.messages.append(
                ("user", question)
            )

            answer = chatbot(question)

            st.session_state.messages.append(
                ("assistant", answer)
            )

            st.rerun()


    with col2:

        if st.button(
            "💡 What is AI?",
            use_container_width=True
        ):

            question = "What is AI?"

            st.session_state.messages.append(
                ("user", question)
            )

            answer = chatbot(question)

            st.session_state.messages.append(
                ("assistant", answer)
            )

            st.rerun()


    with col3:

        if st.button(
            "🌐 Latest Technology",
            use_container_width=True
        ):

            question = "latest technology"

            st.session_state.messages.append(
                ("user", question)
            )

            answer = chatbot(question)

            st.session_state.messages.append(
                ("assistant", answer)
            )

            st.rerun()


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for role, message in st.session_state.messages:

    with st.chat_message(role):

        st.write(message)


# ============================================================
# CONTROLS
# ============================================================

col1, col2 = st.columns(
    [3, 1]
)


with col1:

    st.session_state.tanglish_mode = st.toggle(
        "🗣️ Tanglish Mode",
        value=st.session_state.tanglish_mode
    )


with col2:

    if st.button("🧹 Clear Chat"):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask Purple AI..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    # User message
    st.session_state.messages.append(
        ("user", question)
    )

    with st.chat_message("user"):

        st.write(question)


    # Get answer
    answer = chatbot(question)


    # Tanglish mode indicator
    if st.session_state.tanglish_mode:

        answer = (
            "🗣️ **Tanglish Mode ON** 💜\n\n"
            + answer
        )


    # Save answer
    st.session_state.messages.append(
        ("assistant", answer)
    )


    # Show answer
    with st.chat_message("assistant"):

        st.write(answer)
