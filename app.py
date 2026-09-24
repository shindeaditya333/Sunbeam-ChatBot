import streamlit as st

from login import authenticate, register_user, is_admin
from chatbot import run_chatbot


st.set_page_config(
    page_title="Sunbeam Chatbot",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# SESSION STATE
# =========================================================

if "auth" not in st.session_state:
    st.session_state.auth = False

if "user" not in st.session_state:
    st.session_state.user = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# =========================================================
# AUTHENTICATION PAGE
# =========================================================

if not st.session_state.auth:

    st.title("🤖 Sunbeam Chatbot")

    st.write(
        "Welcome! Login to your account or create a new account."
    )

    login_tab, register_tab = st.tabs(
        [
            "🔐 Login",
            "📝 Create Account"
        ]
    )

    # =====================================================
    # LOGIN TAB
    # =====================================================

    with login_tab:

        st.subheader("Login")

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            use_container_width=True,
            type="primary"
        ):

            if not email or not password:

                st.error(
                    "Please enter your email and password."
                )

            else:

                user = authenticate(
                    email,
                    password
                )

                if user:

                    # -------------------------------------
                    # Save authenticated user
                    # -------------------------------------

                    st.session_state.auth = True

                    st.session_state.user = user

                    st.session_state.user_name = (
                        user["name"]
                    )

                    st.session_state.user_email = (
                        user["email"]
                    )

                    st.session_state.is_admin = (
                        is_admin(user)
                    )

                    st.session_state.chat_history = []

                    st.rerun()

                else:

                    st.error(
                        "Invalid email or password."
                    )

    # =====================================================
    # CREATE ACCOUNT TAB
    # =====================================================

    with register_tab:

        st.subheader("Create Account")

        name = st.text_input(
            "Full Name",
            key="register_name"
        )

        email = st.text_input(
            "Email",
            key="register_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="register_confirm_password"
        )

        if st.button(
            "Create Account",
            use_container_width=True,
            type="primary"
        ):

            if not name or not email or not password:

                st.error(
                    "Please fill in all fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                success, message = register_user(
                    name,
                    email,
                    password
                )

                if success:

                    st.success(
                        message
                    )

                    st.info(
                        "Your account has been created. "
                        "Go to the Login tab to continue."
                    )

                else:

                    st.error(
                        message
                    )


# =========================================================
# CHATBOT
# =========================================================

else:

    run_chatbot()