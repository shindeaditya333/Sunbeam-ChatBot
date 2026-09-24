import hashlib
import json
import re

from config import (
    OUTPUT_JSON,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    COLLECTION_NAME,
)

from embeddings import get_embed_model

from knowledge.vector_store import (
    get_client,
    get_collection,
    delete_collection,
    clear_cache
)


# =========================================================
# TEXT
# =========================================================

def clean_text(text):

    if text is None:
        return ""

    text = str(text)

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def split_large_text(
    text,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP
):

    text = clean_text(text)

    if len(text) <= chunk_size:
        return [text]

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


# =========================================================
# CATEGORY
# =========================================================

def detect_category(
    url,
    title
):

    combined = (
        f"{url} {title}"
    ).lower()

    if "internship" in combined:
        return "internship"

    if "contact" in combined:
        return "contact"

    if "about" in combined:
        return "about"

    if "course" in combined:
        return "course"

    return "general"


# =========================================================
# LOAD JSON
# =========================================================

def load_pages():

    if not OUTPUT_JSON.exists():

        raise FileNotFoundError(
            f"output.json not found at: "
            f"{OUTPUT_JSON}"
        )

    with open(
        OUTPUT_JSON,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if not isinstance(data, list):

        raise ValueError(
            "output.json must contain a list."
        )

    return data


# =========================================================
# CREATE CHUNKS
# =========================================================

def create_chunks(pages):

    chunks = []

    for page_index, page in enumerate(pages):

        if not isinstance(page, dict):
            continue

        url = clean_text(
            page.get("url", "")
        )

        title = clean_text(
            page.get("title")
            or page.get("page_title")
            or "Sunbeam"
        )

        category = detect_category(
            url,
            title
        )

        sections = page.get(
            "sections",
            []
        )

        # -----------------------------------------------
        # YOUR NORMAL COURSE / ABOUT / CONTACT FORMAT
        # -----------------------------------------------

        if sections:

            for section_index, section in enumerate(
                sections
            ):

                section_title = clean_text(
                    section.get(
                        "section_title",
                        "Information"
                    )
                )

                content = section.get(
                    "content",
                    []
                )

                if not isinstance(
                    content,
                    list
                ):
                    content = [content]

                content_lines = []

                for item in content:

                    item = clean_text(item)

                    if item:
                        content_lines.append(item)

                section_text = "\n".join(
                    content_lines
                )

                if not section_text:
                    continue

                parts = split_large_text(
                    section_text
                )

                for part_index, part in enumerate(
                    parts
                ):

                    text = (
                        f"TITLE: {title}\n"
                        f"CATEGORY: {category}\n"
                        f"SECTION: {section_title}\n"
                        f"CONTENT:\n"
                        f"{part}"
                    )

                    chunk_id = hashlib.sha256(
                        (
                            f"{url}|"
                            f"{section_index}|"
                            f"{part_index}"
                        ).encode(
                            "utf-8"
                        )
                    ).hexdigest()

                    chunks.append({
                        "id": chunk_id,
                        "text": text,
                        "url": url,
                        "title": title,
                        "category": category,
                        "section": section_title
                    })

        # -----------------------------------------------
        # FALLBACK FOR INTERNSHIP FORMAT
        # -----------------------------------------------

        else:

            content_parts = []

            for paragraph in page.get(
                "page_paragraphs",
                []
            ):

                text = clean_text(
                    paragraph
                )

                if text:
                    content_parts.append(
                        text
                    )

            for accordion in page.get(
                "accordion_data",
                []
            ):

                accordion_title = clean_text(
                    accordion.get(
                        "title",
                        "Information"
                    )
                )

                paragraph_text = clean_text(
                    accordion.get(
                        "paragraphs",
                        ""
                    )
                )

                if paragraph_text:

                    content_parts.append(
                        f"{accordion_title}: "
                        f"{paragraph_text}"
                    )

                for table in accordion.get(
                    "tables",
                    []
                ):

                    for row in table:

                        if isinstance(row, list):

                            row_text = " | ".join(
                                clean_text(cell)
                                for cell in row
                                if clean_text(cell)
                            )

                            if row_text:
                                content_parts.append(
                                    row_text
                                )

            full_text = "\n".join(
                content_parts
            )

            for part_index, part in enumerate(
                split_large_text(full_text)
            ):

                text = (
                    f"TITLE: {title}\n"
                    f"CATEGORY: {category}\n"
                    f"SECTION: INFORMATION\n"
                    f"CONTENT:\n"
                    f"{part}"
                )

                chunk_id = hashlib.sha256(
                    (
                        f"{url}|"
                        f"fallback|"
                        f"{part_index}"
                    ).encode(
                        "utf-8"
                    )
                ).hexdigest()

                chunks.append({
                    "id": chunk_id,
                    "text": text,
                    "url": url,
                    "title": title,
                    "category": category,
                    "section": "INFORMATION"
                })

    return chunks


# =========================================================
# INDEX
# =========================================================

def rebuild_index():

    pages = load_pages()

    chunks = create_chunks(
        pages
    )

    if not chunks:

        raise ValueError(
            "No chunks generated from output.json."
        )

    delete_collection()

    client = get_client()

    collection = client.get_or_create_collection(
        COLLECTION_NAME
    )

    embed_model = get_embed_model()

    batch_size = 32

    for start in range(
        0,
        len(chunks),
        batch_size
    ):

        batch = chunks[
            start:start + batch_size
        ]

        texts = [
            item["text"]
            for item in batch
        ]

        embeddings = (
            embed_model.embed_documents(
                texts
            )
        )

        collection.upsert(
            ids=[
                item["id"]
                for item in batch
            ],
            embeddings=embeddings,
            documents=texts,
            metadatas=[
                {
                    "url": item["url"],
                    "title": item["title"],
                    "category": item["category"],
                    "section": item["section"]
                }
                for item in batch
            ]
        )

    clear_cache()

    return len(chunks)