import os

import bcrypt
import mysql.connector
from dotenv import load_dotenv


load_dotenv()


# =========================================================
# MYSQL CONFIGURATION
# =========================================================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "sunbeam_chatbot")
DB_USERNAME = os.getenv("DB_USERNAME", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    """
    Connect to the existing MySQL database.

    The database and users table must already exist.
    """

    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USERNAME,
        password=DB_PASSWORD
    )


# =========================================================
# PASSWORD HASHING
# =========================================================

def hash_password(password):
    """
    Hash a password using bcrypt.
    """

    password_bytes = password.encode("utf-8")

    hashed_password = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed_password.decode("utf-8")


# =========================================================
# PASSWORD VERIFICATION
# =========================================================

def verify_password(password, password_hash):
    """
    Verify the entered password against
    the bcrypt password stored in MySQL.
    """

    try:

        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )

    except (ValueError, TypeError):

        return False


# =========================================================
# REGISTER USER
# =========================================================

def register_user(name, email, password):
    """
    Register a new user.

    A new row is inserted into the existing users table.
    New users automatically receive USER role.
    """

    name = name.strip()
    email = email.strip().lower()

    # -----------------------------------------------------
    # Basic validation
    # -----------------------------------------------------

    if not name:
        return False, "Name is required."

    if not email:
        return False, "Email is required."

    if not password:
        return False, "Password is required."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        # -------------------------------------------------
        # Check if email already exists
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            return False, "An account with this email already exists."

        # -------------------------------------------------
        # Hash password
        # -------------------------------------------------

        password_hash = hash_password(password)

        # -------------------------------------------------
        # Insert new user
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password_hash,
                role
            )
            VALUES
            (
                %s,
                %s,
                %s,
                'USER'
            )
            """,
            (
                name,
                email,
                password_hash
            )
        )

        connection.commit()

        return True, "Account created successfully."

    except mysql.connector.Error as error:

        if connection:
            connection.rollback()

        return False, f"Database error: {error}"

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# LOGIN / AUTHENTICATE USER
# =========================================================

def authenticate(email, password):
    """
    Authenticate an existing user.

    Returns user information if login succeeds.
    Returns None if login fails.
    """

    email = email.strip().lower()

    if not email or not password:
        return None

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # -------------------------------------------------
        # Find user by email
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                password_hash,
                role,
                created_at
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        # -------------------------------------------------
        # User does not exist
        # -------------------------------------------------

        if not user:
            return None

        # -------------------------------------------------
        # Verify password
        # -------------------------------------------------

        password_valid = verify_password(
            password,
            user["password_hash"]
        )

        if not password_valid:
            return None

        # -------------------------------------------------
        # Remove password hash before returning user
        # information to the application
        # -------------------------------------------------

        user.pop("password_hash", None)

        return user

    except mysql.connector.Error:
        return None

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# ADMIN CHECK
# =========================================================

def is_admin(user):
    """
    Check whether the logged-in user has ADMIN role.
    """

    if not user:
        return False

    return user.get("role") == "ADMIN"