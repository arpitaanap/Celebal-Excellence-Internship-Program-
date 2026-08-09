import json
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "processed"
    / "structured_chunks.json"
)

VECTOR_DIR = (
    BASE_DIR
    / "vector_store"
)

INDEX_FILE = (
    VECTOR_DIR
    / "brochure.index"
)

METADATA_FILE = (
    VECTOR_DIR
    / "metadata.json"
)


# ============================================================
# MODEL CONFIGURATION
# ============================================================

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# ============================================================
# LOAD STRUCTURED CHUNKS
# ============================================================

def load_chunks():

    if not INPUT_FILE.exists():

        print(
            f"Structured chunks not found: {INPUT_FILE}"
        )

        return []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(file)

    return chunks


# ============================================================
# CREATE VECTOR DATABASE
# ============================================================

def create_vector_store(chunks):

    print("\nLoading embedding model...")

    embedding_model = SentenceTransformer(
        EMBEDDING_MODEL
    )

    print(
        "Embedding model loaded successfully."
    )

    # --------------------------------------------------------
    # Extract chunk text
    # --------------------------------------------------------

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print(
        f"\nGenerating embeddings for {len(texts)} chunks..."
    )

    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    # --------------------------------------------------------
    # Convert to FAISS-compatible format
    # --------------------------------------------------------

    embeddings = embeddings.astype(
        "float32"
    )

    # --------------------------------------------------------
    # Normalize embeddings
    # --------------------------------------------------------

    faiss.normalize_L2(
        embeddings
    )

    print(
        "Embeddings generated successfully."
    )

    print(
        f"Embedding shape: {embeddings.shape}"
    )

    # --------------------------------------------------------
    # Create FAISS index
    # --------------------------------------------------------

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(
        embeddings
    )

    # --------------------------------------------------------
    # Create vector store directory
    # --------------------------------------------------------

    VECTOR_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Save FAISS index
    # --------------------------------------------------------

    faiss.write_index(
        index,
        str(INDEX_FILE)
    )

    # --------------------------------------------------------
    # Save metadata
    # --------------------------------------------------------

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\n" + "=" * 60)

    print(
        "VECTOR DATABASE CREATED"
    )

    print("=" * 60)

    print(
        f"Vectors stored : {index.ntotal}"
    )

    print(
        f"Dimension      : {dimension}"
    )

    print(
        f"FAISS index    : {INDEX_FILE}"
    )

    print(
        f"Metadata       : {METADATA_FILE}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 60)

    print(
        "BUILDING BROCHURE VECTOR DATABASE"
    )

    print("=" * 60)

    chunks = load_chunks()

    if not chunks:

        print(
            "No structured chunks available."
        )

        return

    print(
        f"Loaded chunks: {len(chunks)}"
    )

    create_vector_store(
        chunks
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()