import streamlit as st
from datetime import datetime

from config import (
    MAX_HISTORY_CHARS,
    MAX_ANSWER_CHARS
)

from agents.rag_agent import get_agent


# =========================================================
# SESSION STATE
# =========================================================

def initialize_chat_state():

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = []

    if "active_chat_id" not in st.session_state:
        st.session_state.active_chat_id = None

    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "English"

    if "response_style" not in st.session_state:
        st.session_state.response_style = "Concise"


# =========================================================
# CHAT SESSION HELPERS
# =========================================================

def create_new_chat():

    chat_id = datetime.now().strftime(
        "%Y%m%d%H%M%S%f"
    )

    new_chat = {
        "id": chat_id,
        "title": "New Chat",
        "created_at": datetime.now().strftime(
            "%d %b %Y, %I:%M %p"
        ),
        "messages": []
    }

    st.session_state.chat_sessions.insert(
        0,
        new_chat
    )

    st.session_state.active_chat_id = chat_id

    st.session_state.chat_history = []


def save_current_chat():

    chat_id = st.session_state.get(
        "active_chat_id"
    )

    if not chat_id:
        return

    history = st.session_state.chat_history

    existing_chat = None

    for chat in st.session_state.chat_sessions:

        if chat["id"] == chat_id:
            existing_chat = chat
            break

    if existing_chat is None:
        return

    existing_chat["messages"] = history.copy()

    if history:

        first_question = history[0]["question"]

        if len(first_question) > 32:
            title = (
                first_question[:32]
                + "..."
            )
        else:
            title = first_question

        existing_chat["title"] = title


def load_chat(chat_id):

    selected_chat = None

    for chat in st.session_state.chat_sessions:

        if chat["id"] == chat_id:
            selected_chat = chat
            break

    if selected_chat is None:
        return

    st.session_state.active_chat_id = chat_id

    st.session_state.chat_history = (
        selected_chat["messages"].copy()
    )


def delete_all_chat_history():

    st.session_state.chat_sessions = []

    st.session_state.active_chat_id = None

    st.session_state.chat_history = []


# =========================================================
# PREPARE HISTORY FOR LLM
# =========================================================

def prepare_history():

    history = (
        st.session_state.chat_history
    )

    if not history:
        return []

    selected = []

    total_chars = 0

    # Start from newest.
    for item in reversed(
        history[-8:]
    ):

        question = item[
            "question"
        ]

        answer = item[
            "answer"
        ]

        size = (
            len(question)
            + len(answer)
        )

        if (
            total_chars + size
            > MAX_HISTORY_CHARS
        ):
            break

        selected.append(
            item
        )

        total_chars += size

    selected.reverse()

    messages = []

    for item in selected:

        messages.append({
            "role": "user",
            "content":
                item["question"]
        })

        messages.append({
            "role": "assistant",
            "content":
                item["answer"]
        })

    return messages


# =========================================================
# CLEAN ANSWER
# =========================================================

def clean_answer(answer):

    if not answer:
        return (
            "Information not available "
            "in the provided Sunbeam content."
        )

    # Gemini/LangChain can sometimes return
    # structured content instead of a plain string.
    if isinstance(answer, list):

        text_parts = []

        for item in answer:

            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict):

                text = item.get("text")

                if text:
                    text_parts.append(
                        str(text)
                    )

        answer = "\n".join(
            text_parts
        )

    if not isinstance(answer, str):
        answer = str(answer)

    answer = answer.strip()

    if not answer:
        return (
            "Information not available "
            "in the provided Sunbeam content."
        )

    if len(answer) > MAX_ANSWER_CHARS:

        answer = (
            answer[:MAX_ANSWER_CHARS]
            + "..."
        )

    return answer


# =========================================================
# LANGUAGE / RESPONSE STYLE INSTRUCTIONS
# =========================================================

def get_response_instruction(
    language,
    response_style
):

    language_instruction = {
        "English":
            "Answer in English.",

        "Hindi":
            "Answer in Hindi.",

        "Marathi":
            "Answer in Marathi."
    }

    style_instruction = {
        "Concise":
            (
                "Keep the answer concise and directly "
                "answer the user's question."
            ),

        "Detailed":
            (
                "Provide a detailed answer with useful "
                "explanation, while staying relevant."
            ),

        "Bullet Points":
            (
                "Prefer clear bullet points when "
                "appropriate."
            )
    }

    return (
        language_instruction.get(
            language,
            "Answer in English."
        )
        + "\n"
        + style_instruction.get(
            response_style,
            "Keep the answer concise."
        )
    )


# =========================================================
# ASK QUESTION
# =========================================================

def ask_question(
    question,
    mode,
    language,
    response_style
):

    agent = get_agent(mode)

    history_messages = prepare_history()

    response_instruction = (
        get_response_instruction(
            language,
            response_style
        )
    )

    current_message = {
        "role": "user",
        "content": (
            f"{question}\n\n"
            f"Response instructions:\n"
            f"{response_instruction}"
        )
    }

    messages = (
        history_messages
        + [current_message]
    )

    response = agent.invoke(
        {
            "messages": messages
        },
        config={
            "recursion_limit": 4
        }
    )

    final_message = (
        response["messages"][-1]
    )

    answer = getattr(
        final_message,
        "content",
        ""
    )

    return clean_answer(answer)


# =========================================================
# CHATGPT-STYLE PRINTING EFFECT
# =========================================================

def print_answer_effect(answer):

    placeholder = st.empty()

    displayed_text = ""

    words = answer.split(" ")

    for index, word in enumerate(words):

        if index == 0:
            displayed_text = word

        else:
            displayed_text += (
                " " + word
            )

        placeholder.markdown(
            displayed_text
        )


# =========================================================
# FEEDBACK
# =========================================================

def save_feedback(
    message_index,
    feedback
):

    if (
        message_index
        < len(st.session_state.chat_history)
    ):

        st.session_state.chat_history[
            message_index
        ]["feedback"] = feedback

        save_current_chat()


# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar():

    with st.sidebar:

        # -------------------------------------------------
        # USER
        # -------------------------------------------------

        st.markdown(
            f"### 👤 "
            f"{st.session_state.user_name}"
        )

        st.markdown("---")

        # -------------------------------------------------
        # NEW CHAT
        # -------------------------------------------------

        if st.button(
            "🆕 New Chat",
            use_container_width=True
        ):

            create_new_chat()

            st.rerun()

        # -------------------------------------------------
        # CHAT HISTORY
        # -------------------------------------------------

        st.markdown("---")

        st.markdown(
            "### 💬 Chat History"
        )

        if not st.session_state.chat_sessions:

            st.caption(
                "No previous chats."
            )

        else:

            for chat in (
                st.session_state.chat_sessions
            ):

                title = chat["title"]

                if len(title) > 30:
                    title = (
                        title[:30]
                        + "..."
                    )

                is_active = (
                    chat["id"]
                    ==
                    st.session_state.active_chat_id
                )

                button_label = (
                    "🟢 "
                    if is_active
                    else "💬 "
                ) + title

                if st.button(
                    button_label,
                    key=f"chat_{chat['id']}",
                    use_container_width=True
                ):

                    load_chat(
                        chat["id"]
                    )

                    st.rerun()

        # # -------------------------------------------------
        # # AI MODE
        # # -------------------------------------------------

        # st.markdown("---")

        # st.markdown(
        #     "### 🤖 AI Mode"
        # )

        # mode = st.radio(
        #     "Select AI mode",
        #     [
        #         "online",
        #         "offline"
        #     ],
        #     format_func=lambda value:
        #         (
        #             "🌐 Online — Gemini"
        #             if value == "online"
        #             else "💻 Offline — LM Studio"
        #         ),
        #     horizontal=False
        # )


        # -------------------------------------------------
        # AI MODE
        # -------------------------------------------------

        # Online mode is used for the deployed application.
        # Offline/LM Studio remains available in the code
        # but is hidden from the user interface.

        mode = "online"

        # -------------------------------------------------
        # LANGUAGE
        # -------------------------------------------------

        st.markdown("---")

        st.markdown(
            "### 🌐 Language"
        )

        language = st.selectbox(
            "Response language",
            [
                "English",
                "Hindi",
                "Marathi"
            ],
            index=[
                "English",
                "Hindi",
                "Marathi"
            ].index(
                st.session_state.selected_language
            ),
            label_visibility="collapsed"
        )

        st.session_state.selected_language = (
            language
        )

        # -------------------------------------------------
        # RESPONSE SETTINGS
        # -------------------------------------------------

        st.markdown("---")

        st.markdown(
            "### ⚙️ Response Settings"
        )

        response_style = st.selectbox(
            "Response style",
            [
                "Concise",
                "Detailed",
                "Bullet Points"
            ],
            index=[
                "Concise",
                "Detailed",
                "Bullet Points"
            ].index(
                st.session_state.response_style
            ),
            label_visibility="collapsed"
        )

        st.session_state.response_style = (
            response_style
        )

        # -------------------------------------------------
        # ADMIN
        # -------------------------------------------------

        if st.session_state.get(
            "is_admin",
            False
        ):

            st.markdown("---")

            st.markdown(
                "### 🛠 Admin Controls"
            )

            if st.button(
                "Update Sunbeam Data",
                use_container_width=True
            ):

                with st.spinner(
                    "Scraping Sunbeam website..."
                ):

                    try:

                        from scraping.pipeline import (
                            run_scraping
                        )

                        run_scraping()

                    except Exception as error:

                        st.error(
                            f"Scraping failed: "
                            f"{error}"
                        )

                        return mode

                with st.spinner(
                    "Building optimized knowledge index..."
                ):

                    try:

                        from knowledge.indexer import (
                            rebuild_index
                        )

                        chunk_count = (
                            rebuild_index()
                        )

                        get_agent.clear()

                        st.success(
                            "Sunbeam data updated "
                            f"successfully. "
                            f"{chunk_count} knowledge "
                            "chunks indexed."
                        )

                    except Exception as error:

                        st.error(
                            f"Indexing failed: "
                            f"{error}"
                        )

        # -------------------------------------------------
        # CLEAR CONVERSATION
        # -------------------------------------------------

        st.markdown("---")

        if st.button(
            "🗑 Clear Conversation",
            use_container_width=True
        ):

            delete_all_chat_history()

            st.rerun()

        # -------------------------------------------------
        # ABOUT ASSISTANT
        # -------------------------------------------------

        st.markdown("---")

        with st.expander(
            "ℹ️ About Assistant"
        ):

            st.markdown(
                """
                ### 🤖 Sunbeam AI Assistant

                An AI-powered information assistant
                for Sunbeam Institute.

                **Technology**

                - Retrieval-Augmented Generation (RAG)
                - ChromaDB
                - Gemini
                - LM Studio
                - LangChain

                **AI Modes**

                🌐 **Online**  
                Uses Gemini for response generation.
                """
            )

    return mode


# =========================================================
# MAIN CHATBOT
# =========================================================

def run_chatbot():

    initialize_chat_state()

    st.markdown(
    """
    <style>

    /* Reduce overall sidebar spacing */
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }

    /* Reduce spacing between sidebar elements */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.45rem;
    }

    /* Reduce spacing around horizontal separators */
    section[data-testid="stSidebar"] hr {
        margin: 0.7rem 0;
    }

    /* Reduce heading margins */
    section[data-testid="stSidebar"] h3 {
        margin-top: 0.3rem;
        margin-bottom: 0.3rem;
    }

    /* Reduce paragraph/caption spacing */
    section[data-testid="stSidebar"] p {
        margin-bottom: 0.25rem;
    }

    /* Buttons */
    section[data-testid="stSidebar"] button {
        margin-top: 0.1rem;
        margin-bottom: 0.1rem;
    }

    /* Radio buttons */
    section[data-testid="stSidebar"] [data-testid="stRadio"] {
        margin-top: 0.1rem;
        margin-bottom: 0.3rem;
    }

    /* Select boxes */
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] {
        margin-top: 0.1rem;
        margin-bottom: 0.3rem;
    }

    /* Expander */
    section[data-testid="stSidebar"] [data-testid="stExpander"] {
        margin-top: 0.2rem;
        margin-bottom: 0.2rem;
    }

    </style>
    """,
    unsafe_allow_html=True
    )

    st.title(
        "🤖 Sunbeam Chatbot"
    )

    mode = render_sidebar()

    # =====================================================
    # CURRENT SETTINGS
    # =====================================================

    st.caption(
        f"Mode: **{mode}**"
        f"  |  "
        f"Language: **"
        f"{st.session_state.selected_language}"
        f"**"
        f"  |  "
        f"Style: **"
        f"{st.session_state.response_style}"
        f"**"
    )

    # =====================================================
    # DISPLAY CURRENT CHAT
    # =====================================================

    for index, item in enumerate(
        st.session_state.chat_history
    ):

        # -----------------------------------------------
        # USER
        # -----------------------------------------------

        with st.chat_message(
            "user"
        ):

            st.markdown(
                item["question"]
            )

        # -----------------------------------------------
        # ASSISTANT
        # -----------------------------------------------

        with st.chat_message(
            "assistant"
        ):

            st.markdown(
                item["answer"]
            )

            # -------------------------------------------
            # FEEDBACK
            # -------------------------------------------

            feedback = item.get(
                "feedback"
            )

            if feedback is None:

                col1, col2, col3 = (
                    st.columns(
                        [1, 1, 8]
                    )
                )

                with col1:

                    if st.button(
                        "👍",
                        key=f"like_{index}"
                    ):

                        save_feedback(
                            index,
                            "positive"
                        )

                        st.rerun()

                with col2:

                    if st.button(
                        "👎",
                        key=f"dislike_{index}"
                    ):

                        save_feedback(
                            index,
                            "negative"
                        )

                        st.rerun()

            else:

                if feedback == "positive":

                    st.caption(
                        "👍 Thanks for your feedback!"
                    )

                elif feedback == "negative":

                    st.caption(
                        "👎 Thanks for your feedback!"
                    )

    # =====================================================
    # CHAT INPUT
    # =====================================================

    user_input = st.chat_input(
        "Ask anything about Sunbeam..."
    )

    if user_input:

        user_input = user_input.strip()

        if not user_input:
            return

        # -----------------------------------------------
        # USER MESSAGE
        # -----------------------------------------------

        with st.chat_message(
            "user"
        ):

            st.markdown(
                user_input
            )

        # -----------------------------------------------
        # AI MESSAGE
        # -----------------------------------------------

        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "Thinking..."
            ):

                try:

                    answer = ask_question(
                        question=user_input,
                        mode=mode,
                        language=(
                            st.session_state
                            .selected_language
                        ),
                        response_style=(
                            st.session_state
                            .response_style
                        )
                    )

                except Exception as error:

                    st.error(
                        "Unable to process "
                        f"the request: {error}"
                    )

                    return

            # -------------------------------------------
            # CHATGPT-STYLE PRINTING
            # -------------------------------------------

            print_answer_effect(
                answer
            )

        # -----------------------------------------------
        # SAVE MESSAGE
        # -----------------------------------------------

        st.session_state.chat_history.append({

            "question":
                user_input,

            "answer":
                answer,

            "feedback":
                None
        })

        # Create a chat automatically if
        # the user started typing without
        # explicitly clicking New Chat.
        if not st.session_state.active_chat_id:

            create_new_chat()

            st.session_state.chat_history = [{
                "question":
                    user_input,

                "answer":
                    answer,

                "feedback":
                    None
            }]

        save_current_chat()