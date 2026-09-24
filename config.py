from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

OUTPUT_JSON = DATA_DIR / "output.json"

CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "sunbeam_knowledge"


# =========================================================
# LM STUDIO
# =========================================================
# Used only for local/offline development.
# It is NOT required for deployed/online mode.

LM_STUDIO_BASE_URL = os.getenv(
    "LM_STUDIO_BASE_URL",
    "http://127.0.0.1:1234/v1"
)

LOCAL_LLM_MODEL = os.getenv(
    "LOCAL_LLM_MODEL",
    "openai/gpt-oss-20b"
)


# =========================================================
# EMBEDDING MODEL
# =========================================================
# Gemini is now used for semantic/vector embeddings.
# This makes RAG fully online and removes the dependency
# on LM Studio for embeddings.

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "gemini-embedding-2"
)


# =========================================================
# GEMINI
# =========================================================

GEMINI_API_KEY = (
    os.getenv("GenAI_Gemini_API_Key_1")
    or os.getenv("GEMINI_API_KEY")
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


# =========================================================
# RAG
# =========================================================

# Maximum number of results retrieved from ChromaDB.
MAX_RETRIEVAL_RESULTS = 10

# Maximum amount of retrieved context sent to the LLM.
MAX_CONTEXT_CHARS = 8000


# =========================================================
# CHUNKING
# =========================================================

CHUNK_SIZE = 1800

CHUNK_OVERLAP = 200


# =========================================================
# CHAT HISTORY
# =========================================================

MAX_HISTORY_CHARS = 5000


# =========================================================
# RESPONSE
# =========================================================

MAX_ANSWER_CHARS = 5000