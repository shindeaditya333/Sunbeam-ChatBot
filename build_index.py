from knowledge.indexer import rebuild_index


if __name__ == "__main__":

    print("=" * 60)
    print("SUNBEAM KNOWLEDGE INDEX BUILDER")
    print("=" * 60)

    count = rebuild_index()

    print(
        f"\nSuccessfully indexed "
        f"{count} knowledge chunks."
    )

    print(
        "ChromaDB is ready."
    )