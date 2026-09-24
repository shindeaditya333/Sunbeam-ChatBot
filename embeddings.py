from functools import lru_cache

from google import genai
from google.genai import types

from config import (
    GEMINI_API_KEY,
    EMBEDDING_MODEL
)


# =========================================================
# GEMINI EMBEDDING MODEL
# =========================================================

class GeminiEmbeddingModel:

    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError(
                "Gemini API key is missing."
            )

        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        self.model = EMBEDDING_MODEL

    # -----------------------------------------------------
    # DOCUMENT EMBEDDING
    # -----------------------------------------------------

    def embed_documents(self, texts):

        if not texts:
            return []

        embeddings = []

        for text in texts:

            document_text = (
                "title: none | "
                f"text: {text}"
            )

            result = self.client.models.embed_content(
                model=self.model,
                contents=document_text,
                config=types.EmbedContentConfig(
                    output_dimensionality=768
                )
            )

            embeddings.append(
                result.embeddings[0].values
            )

        return embeddings

    # -----------------------------------------------------
    # QUERY EMBEDDING
    # -----------------------------------------------------

    def embed_query(self, query):

        if not query or not query.strip():
            raise ValueError(
                "Search query cannot be empty."
            )

        query_text = (
            "task: search result | "
            f"query: {query}"
        )

        result = self.client.models.embed_content(
            model=self.model,
            contents=query_text,
            config=types.EmbedContentConfig(
                output_dimensionality=768
            )
        )

        return result.embeddings[0].values


# =========================================================
# CACHED EMBEDDING MODEL
# =========================================================

@lru_cache(maxsize=1)
def get_embed_model():

    return GeminiEmbeddingModel()