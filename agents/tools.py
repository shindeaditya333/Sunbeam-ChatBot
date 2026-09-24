from langchain.tools import tool

from config import MAX_CONTEXT_CHARS, MAX_RETRIEVAL_RESULTS
from embeddings import get_embed_model
from knowledge.vector_store import get_collection


def create_search_tool():

    @tool
    def search_sunbeam_knowledge(query: str) -> str:
        """
        Search the Sunbeam knowledge base using semantic
        vector retrieval.
        """

        if not query or not query.strip():
            return "No search query was provided."

        collection = get_collection()

        if collection.count() == 0:
            return "The Sunbeam knowledge base is empty."

        embed_model = get_embed_model()

        # --------------------------------------------------
        # Create query embedding
        # --------------------------------------------------

        query_embedding = embed_model.embed_query(query)

        # --------------------------------------------------
        # Retrieve results from the knowledge base
        # --------------------------------------------------

        retrieval_limit = min(
            MAX_RETRIEVAL_RESULTS,
            collection.count()
        )

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=retrieval_limit,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        if not documents:
            return (
                "Information not available in the provided "
                "Sunbeam content."
            )

        # --------------------------------------------------
        # Build context for the LLM
        # --------------------------------------------------

        output = []
        total_chars = 0

        for index, document in enumerate(
            documents,
            start=1
        ):

            metadata = (
                metadatas[index - 1]
                if index - 1 < len(metadatas)
                else {}
            )

            title = metadata.get(
                "title",
                "Sunbeam"
            )

            category = metadata.get(
                "category",
                "general"
            )

            section = metadata.get(
                "section",
                "Information"
            )

            url = metadata.get(
                "url",
                ""
            )

            block = (
                f"SOURCE {index}\n"
                f"TITLE: {title}\n"
                f"CATEGORY: {category}\n"
                f"SECTION: {section}\n"
                f"URL: {url}\n\n"
                f"CONTENT:\n"
                f"{document}"
            )

            remaining = (
                MAX_CONTEXT_CHARS
                - total_chars
            )

            if remaining <= 0:
                break

            # Keep complete chunks only.
            # Don't cut a chunk halfway through.
            if len(block) > remaining:
                break

            output.append(block)
            total_chars += len(block)

        if not output:
            return (
                "Information not available in the provided "
                "Sunbeam content."
            )

        return "\n\n---\n\n".join(output)

    return search_sunbeam_knowledge