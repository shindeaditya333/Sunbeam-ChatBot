from functools import lru_cache

import chromadb

from config import (
    CHROMA_DIR,
    COLLECTION_NAME
)


@lru_cache(maxsize=1)
def get_client():

    return chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )


@lru_cache(maxsize=1)
def get_collection():

    client = get_client()

    return client.get_or_create_collection(
        COLLECTION_NAME
    )


def clear_cache():

    get_collection.cache_clear()
    get_client.cache_clear()


def collection_size():

    collection = get_collection()

    return collection.count()


def delete_collection():

    client = get_client()

    try:
        client.delete_collection(
            COLLECTION_NAME
        )
    except Exception:
        pass

    clear_cache()