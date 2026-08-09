import json
import re
from pathlib import Path
from collections import Counter

import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

VECTOR_DIR = BASE_DIR / "vector_store"

INDEX_FILE = VECTOR_DIR / "brochure.index"
METADATA_FILE = VECTOR_DIR / "metadata.json"


# ============================================================
# MODEL CONFIGURATION
# ============================================================

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


# ============================================================
# RETRIEVAL CONFIGURATION
# ============================================================

VECTOR_TOP_K = 50
KEYWORD_TOP_K = 50

RERANK_TOP_K = 15

DEFAULT_FINAL_TOP_K = 5


# ============================================================
# HYBRID RETRIEVER
# ============================================================

class HybridRetriever:

    def __init__(self):

        print("\nLoading retrieval system...")

        # ----------------------------------------------------
        # Check files
        # ----------------------------------------------------

        if not INDEX_FILE.exists():

            raise FileNotFoundError(
                f"FAISS index not found: {INDEX_FILE}"
            )

        if not METADATA_FILE.exists():

            raise FileNotFoundError(
                f"Metadata file not found: {METADATA_FILE}"
            )

        # ----------------------------------------------------
        # Load FAISS
        # ----------------------------------------------------

        self.index = faiss.read_index(
            str(INDEX_FILE)
        )

        # ----------------------------------------------------
        # Load metadata
        # ----------------------------------------------------

        with open(
            METADATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            self.metadata = json.load(file)

        print(
            f"✓ Loaded {len(self.metadata)} chunks"
        )

        # ----------------------------------------------------
        # Load embedding model
        # ----------------------------------------------------

        print(
            "\nLoading embedding model..."
        )

        self.embedding_model = SentenceTransformer(
            EMBEDDING_MODEL
        )

        print(
            "✓ Embedding model loaded"
        )

        # ----------------------------------------------------
        # Load reranker
        # ----------------------------------------------------

        print(
            "\nLoading re-ranking model..."
        )

        self.reranker = CrossEncoder(
            RERANKER_MODEL
        )

        print(
            "✓ Re-ranking model loaded"
        )

        print(
            "✓ Retrieval system ready"
        )


    # ========================================================
    # NORMALIZE TEXT
    # ========================================================

    def normalize_text(
        self,
        text
    ):

        text = str(text).lower()

        # ----------------------------------------------------
        # Fix OCR spacing
        #
        # Example:
        #
        # "S E A T"
        #
        # becomes:
        #
        # "SEAT"
        # ----------------------------------------------------

        text = re.sub(
            r"\b(?:[a-z]\s+){2,}[a-z]\b",
            lambda match: match.group(0).replace(" ", ""),
            text
        )

        # ----------------------------------------------------
        # Normalize whitespace
        # ----------------------------------------------------

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()


    # ========================================================
    # TOKENIZATION
    # ========================================================

    def tokenize(
        self,
        text
    ):

        text = self.normalize_text(
            text
        )

        words = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text
        )

        # ----------------------------------------------------
        # Generic stop words
        #
        # IMPORTANT:
        #
        # Do NOT remove meaningful vehicle words such as:
        #
        # roof
        # seat
        # safety
        # feature
        # passenger
        # engine
        # brake
        # etc.
        # ----------------------------------------------------

        stop_words = {

            "the",
            "is",
            "are",
            "was",
            "were",

            "a",
            "an",

            "this",
            "that",
            "these",
            "those",

            "does",
            "do",
            "did",

            "what",
            "which",
            "who",
            "where",
            "when",
            "why",
            "how",

            "many",
            "much",

            "can",
            "could",
            "would",
            "should",

            "have",
            "has",
            "had",

            "it",
            "its",

            "i",
            "me",
            "my",
            "we",
            "our",

            "you",
            "your",

            "there",
            "their",

            "be",
            "been",
            "being",

            "tell",
            "give",
            "show",

            "please",

            "about",
            "for",
            "from",
            "with",
            "without",

            "and",
            "or",
            "but",

            "of",
            "to",
            "in",
            "on",
            "at",
            "by",
            "as",

            "does",
            "come",
            "comes"
        }

        return [
            word
            for word in words
            if word not in stop_words
        ]


    # ========================================================
    # QUERY PHRASES
    # ========================================================

    def extract_phrases(
        self,
        query
    ):

        normalized = self.normalize_text(
            query
        )

        words = self.tokenize(
            normalized
        )

        phrases = set()

        # ----------------------------------------------------
        # Single meaningful words
        # ----------------------------------------------------

        for word in words:

            if len(word) >= 3:

                phrases.add(
                    word
                )

        # ----------------------------------------------------
        # Two-word phrases
        # ----------------------------------------------------

        for i in range(
            len(words) - 1
        ):

            phrase = (
                words[i]
                + " "
                + words[i + 1]
            )

            phrases.add(
                phrase
            )

        # ----------------------------------------------------
        # Three-word phrases
        # ----------------------------------------------------

        for i in range(
            len(words) - 2
        ):

            phrase = (
                words[i]
                + " "
                + words[i + 1]
                + " "
                + words[i + 2]
            )

            phrases.add(
                phrase
            )

        return phrases


    # ========================================================
    # METADATA FILTERING
    # ========================================================

    def filter_metadata(
        self,
        brand,
        model
    ):

        brand = (
            str(brand)
            .lower()
            .strip()
        )

        model = (
            str(model)
            .lower()
            .strip()
        )

        allowed_indices = []

        for index, item in enumerate(
            self.metadata
        ):

            item_brand = (
                str(
                    item.get(
                        "brand",
                        ""
                    )
                )
                .lower()
                .strip()
            )

            item_model = (
                str(
                    item.get(
                        "model",
                        ""
                    )
                )
                .lower()
                .strip()
            )

            if (
                item_brand == brand
                and item_model == model
            ):

                allowed_indices.append(
                    index
                )

        return allowed_indices


    # ========================================================
    # KEYWORD SEARCH
    # ========================================================

    def keyword_search(
        self,
        query,
        allowed_indices,
        top_k=KEYWORD_TOP_K
    ):

        query_tokens = self.tokenize(
            query
        )

        query_words = set(
            query_tokens
        )

        if not query_words:

            return []

        query_phrases = (
            self.extract_phrases(
                query
            )
        )

        results = []

        for index in allowed_indices:

            item = self.metadata[index]

            text = str(
                item.get(
                    "text",
                    ""
                )
            )

            if not text:

                continue

            normalized_text = (
                self.normalize_text(
                    text
                )
            )

            text_words = set(
                self.tokenize(
                    normalized_text
                )
            )

            if not text_words:

                continue

            # ------------------------------------------------
            # Exact token matching
            # ------------------------------------------------

            matched_words = (
                query_words.intersection(
                    text_words
                )
            )

            # ------------------------------------------------
            # Token overlap
            # ------------------------------------------------

            if query_words:

                token_score = (
                    len(matched_words)
                    / len(query_words)
                )

            else:

                token_score = 0.0

            # ------------------------------------------------
            # Phrase matching
            # ------------------------------------------------

            matched_phrases = []

            for phrase in query_phrases:

                if " " in phrase:

                    if phrase in normalized_text:

                        matched_phrases.append(
                            phrase
                        )

            phrase_score = 0.0

            if matched_phrases:

                phrase_score = min(
                    len(matched_phrases) * 0.20,
                    0.60
                )

            # ------------------------------------------------
            # Exact query match
            # ------------------------------------------------

            exact_query_score = 0.0

            normalized_query = (
                self.normalize_text(
                    query
                )
            )

            if (
                normalized_query
                and normalized_query
                in normalized_text
            ):

                exact_query_score = 0.50

            # ------------------------------------------------
            # Final keyword score
            # ------------------------------------------------

            keyword_score = (
                token_score
                + phrase_score
                + exact_query_score
            )

            if keyword_score <= 0:

                continue

            result = item.copy()

            result["_index"] = index

            result["keyword_score"] = (
                float(keyword_score)
            )

            result["matched_keywords"] = (
                sorted(
                    matched_words
                )
            )

            result["matched_phrases"] = (
                sorted(
                    matched_phrases
                )
            )

            results.append(
                result
            )

        # ----------------------------------------------------
        # Sort
        # ----------------------------------------------------

        results.sort(
            key=lambda item: (
                item.get(
                    "keyword_score",
                    0.0
                )
            ),
            reverse=True
        )

        return results[:top_k]


    # ========================================================
    # VECTOR SEARCH
    # ========================================================

    def vector_search(
        self,
        query,
        allowed_indices,
        top_k=VECTOR_TOP_K
    ):

        if not allowed_indices:

            return []

        # ----------------------------------------------------
        # Encode query
        # ----------------------------------------------------

        query_embedding = (
            self.embedding_model.encode(
                [query],
                convert_to_numpy=True
            )
        )

        query_embedding = (
            query_embedding.astype(
                "float32"
            )
        )

        # ----------------------------------------------------
        # Normalize
        # ----------------------------------------------------

        faiss.normalize_L2(
            query_embedding
        )

        # ----------------------------------------------------
        # Retrieve a large candidate pool
        # ----------------------------------------------------

        search_k = min(
            max(
                top_k * 8,
                100
            ),
            self.index.ntotal
        )

        scores, indices = (
            self.index.search(
                query_embedding,
                search_k
            )
        )

        allowed_set = set(
            allowed_indices
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            index = int(
                index
            )

            if index not in allowed_set:

                continue

            item = self.metadata[
                index
            ].copy()

            item["_index"] = index

            item["vector_score"] = (
                float(score)
            )

            results.append(
                item
            )

            if len(results) >= top_k:

                break

        return results


    # ========================================================
    # MERGE RESULTS
    # ========================================================

    def merge_results(
        self,
        vector_results,
        keyword_results
    ):

        merged = {}

        # ----------------------------------------------------
        # Vector results
        # ----------------------------------------------------

        for item in vector_results:

            index = item["_index"]

            merged[index] = (
                item.copy()
            )

            merged[index][
                "keyword_score"
            ] = 0.0

            merged[index][
                "matched_keywords"
            ] = []

            merged[index][
                "matched_phrases"
            ] = []


        # ----------------------------------------------------
        # Keyword results
        # ----------------------------------------------------

        for item in keyword_results:

            index = item["_index"]

            if index not in merged:

                merged[index] = (
                    item.copy()
                )

                merged[index][
                    "vector_score"
                ] = 0.0

            else:

                merged[index][
                    "keyword_score"
                ] = item.get(
                    "keyword_score",
                    0.0
                )

                merged[index][
                    "matched_keywords"
                ] = item.get(
                    "matched_keywords",
                    []
                )

                merged[index][
                    "matched_phrases"
                ] = item.get(
                    "matched_phrases",
                    []
                )

        return list(
            merged.values()
        )


    # ========================================================
    # PRE-RERANK SCORE
    # ========================================================

    def calculate_hybrid_score(
        self,
        item
    ):

        vector_score = float(
            item.get(
                "vector_score",
                0.0
            )
        )

        keyword_score = float(
            item.get(
                "keyword_score",
                0.0
            )
        )

        # ----------------------------------------------------
        # Vector score is cosine similarity.
        #
        # Keyword score is independently calculated.
        #
        # We use a light-weight hybrid score only to
        # prepare candidates before CrossEncoder.
        # ----------------------------------------------------

        hybrid_score = (
            vector_score * 0.65
            + keyword_score * 0.35
        )

        return hybrid_score


    # ========================================================
    # CROSS ENCODER RERANKING
    # ========================================================

    def rerank(
        self,
        query,
        candidates,
        top_k=RERANK_TOP_K
    ):

        if not candidates:

            return []

        # ----------------------------------------------------
        # Calculate hybrid score
        # ----------------------------------------------------

        for item in candidates:

            item["hybrid_score"] = (
                self.calculate_hybrid_score(
                    item
                )
            )

        # ----------------------------------------------------
        # Keep a reasonably large candidate pool
        # ----------------------------------------------------

        candidates.sort(
            key=lambda item: (
                item.get(
                    "hybrid_score",
                    0.0
                )
            ),
            reverse=True
        )

        candidates = candidates[
            :max(
                top_k * 3,
                30
            )
        ]

        # ----------------------------------------------------
        # Create CrossEncoder pairs
        # ----------------------------------------------------

        pairs = []

        for item in candidates:

            pairs.append(
                (
                    query,
                    item.get(
                        "text",
                        ""
                    )
                )
            )

        # ----------------------------------------------------
        # CrossEncoder
        # ----------------------------------------------------

        scores = self.reranker.predict(
            pairs
        )

        # ----------------------------------------------------
        # Save rerank score
        # ----------------------------------------------------

        for item, score in zip(
            candidates,
            scores
        ):

            item["rerank_score"] = (
                float(score)
            )

        # ----------------------------------------------------
        # Sort by reranker
        # ----------------------------------------------------

        candidates.sort(
            key=lambda item: (
                item.get(
                    "rerank_score",
                    -999
                )
            ),
            reverse=True
        )

        return candidates[:top_k]


    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    def remove_duplicates(
        self,
        results
    ):

        unique_results = []

        seen_text = set()

        for item in results:

            text = str(
                item.get(
                    "text",
                    ""
                )
            ).strip()

            if not text:

                continue

            normalized = (
                self.normalize_text(
                    text
                )
            )

            if normalized in seen_text:

                continue

            seen_text.add(
                normalized
            )

            unique_results.append(
                item
            )

        return unique_results


    # ========================================================
    # REMOVE VERY WEAK RESULTS
    # ========================================================

    def remove_weak_results(
        self,
        results
    ):

        if not results:

            return []

        # ----------------------------------------------------
        # Do NOT aggressively remove results.
        #
        # Some valid brochure answers may have low scores.
        #
        # We only remove results when they are clearly
        # unrelated to both semantic and lexical retrieval.
        # ----------------------------------------------------

        filtered = []

        for item in results:

            vector_score = float(
                item.get(
                    "vector_score",
                    0.0
                )
            )

            keyword_score = float(
                item.get(
                    "keyword_score",
                    0.0
                )
            )

            rerank_score = float(
                item.get(
                    "rerank_score",
                    -999
                )
            )

            # ------------------------------------------------
            # Keep if at least one retrieval signal is useful.
            # ------------------------------------------------

            if (
                vector_score >= 0.20
                or keyword_score > 0
                or rerank_score > -5
            ):

                filtered.append(
                    item
                )

        return filtered


    # ========================================================
    # FINAL SEARCH PIPELINE
    # ========================================================

    def search(
        self,
        query,
        brand,
        model,
        top_k=DEFAULT_FINAL_TOP_K
    ):

        # ====================================================
        # STEP 1
        # Vehicle metadata filtering
        # ====================================================

        allowed_indices = (
            self.filter_metadata(
                brand,
                model
            )
        )

        if not allowed_indices:

            return []


        # ====================================================
        # STEP 2
        # Semantic retrieval
        # ====================================================

        vector_results = (
            self.vector_search(
                query=query,
                allowed_indices=allowed_indices,
                top_k=VECTOR_TOP_K
            )
        )


        # ====================================================
        # STEP 3
        # Keyword / phrase retrieval
        # ====================================================

        keyword_results = (
            self.keyword_search(
                query=query,
                allowed_indices=allowed_indices,
                top_k=KEYWORD_TOP_K
            )
        )


        # ====================================================
        # STEP 4
        # Merge
        # ====================================================

        candidates = (
            self.merge_results(
                vector_results,
                keyword_results
            )
        )

        if not candidates:

            return []


        # ====================================================
        # STEP 5
        # Hybrid pre-ranking
        # ====================================================

        for item in candidates:

            item["hybrid_score"] = (
                self.calculate_hybrid_score(
                    item
                )
            )


        candidates.sort(
            key=lambda item: (
                item.get(
                    "hybrid_score",
                    0.0
                )
            ),
            reverse=True
        )


        # ====================================================
        # STEP 6
        # CrossEncoder reranking
        # ====================================================

        candidates = (
            self.rerank(
                query=query,
                candidates=candidates,
                top_k=RERANK_TOP_K
            )
        )


        # ====================================================
        # STEP 7
        # Remove duplicates
        # ====================================================

        candidates = (
            self.remove_duplicates(
                candidates
            )
        )


        # ====================================================
        # STEP 8
        # Remove clearly weak results
        # ====================================================

        candidates = (
            self.remove_weak_results(
                candidates
            )
        )


        # ====================================================
        # STEP 9
        # Final context
        # ====================================================

        return candidates[:top_k]


# ============================================================
# TEST
# ============================================================

def main():

    print(
        "\n" + "=" * 70
    )

    print(
        "DRIVE WISE HYBRID RETRIEVAL TEST"
    )

    print(
        "=" * 70
    )

    retriever = HybridRetriever()


    # --------------------------------------------------------
    # Vehicle
    # --------------------------------------------------------

    brand = input(
        "\nEnter brand: "
    ).strip()

    model = input(
        "Enter model: "
    ).strip()


    # --------------------------------------------------------
    # Question
    # --------------------------------------------------------

    query = input(
        "Enter question: "
    ).strip()


    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    results = retriever.search(
        query=query,
        brand=brand,
        model=model,
        top_k=5
    )


    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        f"Retrieved {len(results)} final chunks"
    )

    print(
        "=" * 70
    )


    if not results:

        print(
            "\nNo relevant brochure information found."
        )

        return


    for number, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\nResult {number}"
        )

        print(
            "-" * 70
        )

        print(
            f"Brand       : "
            f"{result.get('brand')}"
        )

        print(
            f"Model       : "
            f"{result.get('model')}"
        )

        print(
            f"Section     : "
            f"{result.get('section')}"
        )

        print(
            f"Page        : "
            f"{result.get('page')}"
        )

        print(
            f"Brochure    : "
            f"{result.get('brochure')}"
        )

        print(
            f"Vector      : "
            f"{result.get('vector_score', 0):.4f}"
        )

        print(
            f"Keyword     : "
            f"{result.get('keyword_score', 0):.4f}"
        )

        print(
            f"Matched     : "
            f"{result.get('matched_keywords', [])}"
        )

        print(
            f"Phrase      : "
            f"{result.get('matched_phrases', [])}"
        )

        print(
            f"Hybrid      : "
            f"{result.get('hybrid_score', 0):.4f}"
        )

        print(
            f"Rerank      : "
            f"{result.get('rerank_score', 0):.4f}"
        )

        print(
            f"\nText:\n"
            f"{result.get('text', '')}"
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()