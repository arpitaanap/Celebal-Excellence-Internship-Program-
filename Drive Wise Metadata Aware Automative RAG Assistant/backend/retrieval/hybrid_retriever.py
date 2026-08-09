import json
import re
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

VECTOR_DIR = BASE_DIR / "vector_store"

INDEX_FILE = VECTOR_DIR / "brochure.index"
METADATA_FILE = VECTOR_DIR / "metadata.json"


# ============================================================
# MODELS
# ============================================================

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


# ============================================================
# RETRIEVAL SETTINGS
# ============================================================

VECTOR_TOP_K = 30
KEYWORD_TOP_K = 30
RERANK_TOP_K = 15
FINAL_TOP_K = 5

# Minimum similarity below which semantic results are weak.
MIN_VECTOR_SCORE = 0.15


# ============================================================
# QUERY ALIASES
#
# Keep this relatively small.
# The purpose is to handle common automotive terminology,
# not to create hundreds of noisy search terms.
# ============================================================

QUERY_ALIASES = {

    "sunroof": [
        "sunroof",
        "sun roof",
        "moonroof",
        "moon roof",
        "panoramic roof",
        "glass roof"
    ],

    "seats": [
        "seat",
        "seats",
        "seating",
        "seating capacity"
    ],

    "seat": [
        "seat",
        "seats",
        "seating",
        "seating capacity"
    ],

    "airbags": [
        "airbag",
        "airbags"
    ],

    "airbag": [
        "airbag",
        "airbags"
    ],

    "safety": [
        "safety",
        "airbag",
        "abs",
        "ebd",
        "esp",
        "brake assist",
        "hill hold",
        "hill descent",
        "seatbelt",
        "parking sensors"
    ],

    "infotainment": [
        "infotainment",
        "touchscreen",
        "touch screen",
        "display"
    ],

    "touchscreen": [
        "touchscreen",
        "touch screen",
        "infotainment",
        "display"
    ],

    "carplay": [
        "apple carplay",
        "carplay"
    ],

    "android": [
        "android auto",
        "android"
    ],

    "cruise": [
        "cruise control",
        "cruise"
    ],

    "engine": [
        "engine",
        "petrol engine",
        "diesel engine",
        "power",
        "torque"
    ],

    "power": [
        "power",
        "bhp",
        "ps",
        "kw"
    ],

    "torque": [
        "torque",
        "nm"
    ],

    "mileage": [
        "mileage",
        "fuel economy",
        "fuel efficiency",
        "kmpl"
    ],

    "automatic": [
        "automatic",
        "automatic transmission",
        "automatic gearbox"
    ],

    "manual": [
        "manual",
        "manual transmission",
        "manual gearbox"
    ],

    "tyres": [
        "tyre",
        "tyres",
        "tire",
        "tires",
        "wheel",
        "wheels"
    ],

    "wheels": [
        "wheel",
        "wheels",
        "alloy wheels",
        "tyres",
        "tires"
    ],

    "ac": [
        "ac",
        "air conditioning",
        "air conditioner",
        "climate control"
    ],

    "parking": [
        "parking",
        "parking sensor",
        "parking sensors",
        "rear parking sensors"
    ],

    "ground clearance": [
        "ground clearance",
        "clearance"
    ],

    "boot": [
        "boot",
        "boot space",
        "luggage space"
    ],

    "fuel tank": [
        "fuel tank",
        "tank capacity"
    ]
}


# ============================================================
# QUESTION TYPES
# ============================================================

EXISTENCE_PATTERNS = [
    r"\bdoes\b.*\bhave\b",
    r"\bhas\b.*\b",
    r"\bis\b.*\bavailable\b",
    r"\bavailable\b",
    r"\bcomes with\b",
    r"\bget\b",
    r"\bgets\b",
    r"\bfeature\b"
]


# ============================================================
# HYBRID RETRIEVER
# ============================================================

class HybridRetriever:

    def __init__(self):

        print("\nLoading retrieval system...")

        # ----------------------------------------------------
        # Validate files
        # ----------------------------------------------------

        if not INDEX_FILE.exists():
            raise FileNotFoundError(
                f"FAISS index not found:\n{INDEX_FILE}"
            )

        if not METADATA_FILE.exists():
            raise FileNotFoundError(
                f"Metadata file not found:\n{METADATA_FILE}"
            )

        # ----------------------------------------------------
        # Load FAISS
        # ----------------------------------------------------

        self.index = faiss.read_index(
            str(INDEX_FILE)
        )

        print(
            f"✓ FAISS index loaded: "
            f"{self.index.ntotal} vectors"
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
            f"✓ Metadata loaded: "
            f"{len(self.metadata)} chunks"
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


    # ========================================================
    # NORMALIZE TEXT
    # ========================================================

    @staticmethod
    def normalize_text(text):

        if text is None:
            return ""

        text = str(text).lower()

        # Normalize hyphens
        text = text.replace("-", " ")

        # Normalize underscores
        text = text.replace("_", " ")

        # Normalize whitespace
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()


    # ========================================================
    # TOKENIZE
    # ========================================================

    def tokenize(self, text):

        text = self.normalize_text(
            text
        )

        tokens = re.findall(
            r"\b[a-z0-9]+\b",
            text
        )

        stop_words = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",

            "does",
            "do",
            "did",

            "has",
            "have",
            "had",

            "what",
            "which",
            "who",
            "where",
            "when",
            "why",
            "how",

            "many",
            "much",

            "this",
            "that",
            "these",
            "those",

            "it",
            "its",

            "of",
            "to",
            "for",
            "from",
            "with",

            "in",
            "on",
            "at",
            "by",

            "and",
            "or",

            "can",
            "could",
            "would",
            "will",

            "please",

            # Vehicle metadata should not affect
            # content matching.
            "mahindra",
            "thar"
        }

        return [
            token
            for token in tokens
            if token not in stop_words
        ]


    # ========================================================
    # FILTER BY BRAND + MODEL
    # ========================================================

    def filter_metadata(
        self,
        brand,
        model
    ):

        brand = self.normalize_text(
            brand
        )

        model = self.normalize_text(
            model
        )

        allowed_indices = []

        for index, item in enumerate(
            self.metadata
        ):

            item_brand = self.normalize_text(
                item.get("brand", "")
            )

            item_model = self.normalize_text(
                item.get("model", "")
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
    # DETECT FEATURES
    # ========================================================

    def detect_features(
        self,
        query
    ):

        normalized_query = self.normalize_text(
            query
        )

        detected = []

        for feature, aliases in QUERY_ALIASES.items():

            feature_text = self.normalize_text(
                feature
            )

            if feature_text in normalized_query:

                detected.append(
                    feature
                )

                continue

            for alias in aliases:

                alias_text = self.normalize_text(
                    alias
                )

                if alias_text in normalized_query:

                    detected.append(
                        feature
                    )

                    break

        # Remove duplicates while preserving order
        return list(
            dict.fromkeys(detected)
        )


    # ========================================================
    # DETECT EXISTENCE QUESTION
    # ========================================================

    def is_existence_question(
        self,
        query
    ):

        query = self.normalize_text(
            query
        )

        return any(
            re.search(
                pattern,
                query
            )
            for pattern in EXISTENCE_PATTERNS
        )


    # ========================================================
    # EXPAND QUERY
    # ========================================================

    def expand_query(
        self,
        query
    ):

        normalized_query = self.normalize_text(
            query
        )

        expanded = []

        # Original query first
        expanded.append(
            normalized_query
        )

        detected_features = self.detect_features(
            query
        )

        # Add aliases only for detected concepts
        for feature in detected_features:

            aliases = QUERY_ALIASES.get(
                feature,
                []
            )

            expanded.extend(
                aliases
            )

        # Remove duplicates
        final_queries = []

        seen = set()

        for item in expanded:

            item = self.normalize_text(
                item
            )

            if not item:
                continue

            if item in seen:
                continue

            seen.add(item)

            final_queries.append(
                item
            )

        return final_queries


    # ========================================================
    # EXACT / KEYWORD SEARCH
    # ========================================================

    def keyword_search(
        self,
        query,
        allowed_indices,
        top_k=KEYWORD_TOP_K
    ):

        if not allowed_indices:
            return []

        query_tokens = set(
            self.tokenize(query)
        )

        expanded_queries = self.expand_query(
            query
        )

        results = []

        for index in allowed_indices:

            item = self.metadata[index]

            text = str(
                item.get(
                    "text",
                    ""
                )
            ).strip()

            if not text:
                continue

            normalized_text = self.normalize_text(
                text
            )

            text_tokens = set(
                self.tokenize(
                    normalized_text
                )
            )

            matched_tokens = (
                query_tokens.intersection(
                    text_tokens
                )
            )

            matched_aliases = []

            for expanded_query in expanded_queries:

                # For multi-word aliases, phrase matching
                # is more meaningful than token matching.
                if (
                    len(expanded_query) >= 3
                    and expanded_query in normalized_text
                ):

                    matched_aliases.append(
                        expanded_query
                    )

            if (
                not matched_tokens
                and not matched_aliases
            ):
                continue

            # ------------------------------------------------
            # Score
            # ------------------------------------------------

            score = 0.0

            # Original query token coverage
            if query_tokens:

                coverage = (
                    len(matched_tokens)
                    / len(query_tokens)
                )

                score += (
                    coverage * 2.0
                )

            # Exact alias matches
            score += (
                len(
                    set(matched_aliases)
                ) * 2.5
            )

            # Exact complete query phrase
            normalized_query = self.normalize_text(
                query
            )

            if (
                normalized_query
                and normalized_query in normalized_text
            ):

                score += 4.0

            result = item.copy()

            result["_index"] = index

            result["keyword_score"] = float(
                score
            )

            result["matched_keywords"] = sorted(
                set(
                    list(matched_tokens)
                    + matched_aliases
                )
            )

            # Direct evidence means the actual requested
            # feature/concept appears in the chunk.
            result["direct_match"] = (
                len(matched_aliases) > 0
            )

            results.append(
                result
            )

        results.sort(
            key=lambda x: (
                x.get(
                    "direct_match",
                    False
                ),
                x.get(
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
        # Encode
        # ----------------------------------------------------

        embedding = (
            self.embedding_model.encode(
                [query],
                convert_to_numpy=True
            )
        )

        embedding = embedding.astype(
            "float32"
        )

        # ----------------------------------------------------
        # Normalize
        # ----------------------------------------------------

        faiss.normalize_L2(
            embedding
        )

        # ----------------------------------------------------
        # Search broad candidate pool
        # ----------------------------------------------------

        search_k = min(
            max(
                top_k * 10,
                100
            ),
            self.index.ntotal
        )

        scores, indices = (
            self.index.search(
                embedding,
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

            index = int(index)

            if index not in allowed_set:
                continue

            score = float(
                score
            )

            # Ignore extremely weak semantic matches
            if score < MIN_VECTOR_SCORE:
                continue

            item = self.metadata[
                index
            ].copy()

            item["_index"] = index

            item["vector_score"] = score

            results.append(
                item
            )

            if len(results) >= top_k:
                break

        return results


    # ========================================================
    # MERGE CANDIDATES
    # ========================================================

    def merge_candidates(
        self,
        vector_results,
        keyword_results
    ):

        merged = {}

        # ----------------------------------------------------
        # Vector candidates
        # ----------------------------------------------------

        for item in vector_results:

            index = item["_index"]

            merged[index] = item.copy()

            merged[index].setdefault(
                "vector_score",
                0.0
            )

            merged[index].setdefault(
                "keyword_score",
                0.0
            )

            merged[index].setdefault(
                "matched_keywords",
                []
            )

            merged[index].setdefault(
                "direct_match",
                False
            )

        # ----------------------------------------------------
        # Keyword candidates
        # ----------------------------------------------------

        for item in keyword_results:

            index = item["_index"]

            if index not in merged:

                merged[index] = item.copy()

                merged[index].setdefault(
                    "vector_score",
                    0.0
                )

            else:

                merged[index]["keyword_score"] = max(
                    merged[index].get(
                        "keyword_score",
                        0.0
                    ),
                    item.get(
                        "keyword_score",
                        0.0
                    )
                )

                merged[index]["matched_keywords"] = (
                    item.get(
                        "matched_keywords",
                        []
                    )
                )

                merged[index]["direct_match"] = (
                    merged[index].get(
                        "direct_match",
                        False
                    )
                    or
                    item.get(
                        "direct_match",
                        False
                    )
                )

        return list(
            merged.values()
        )


    # ========================================================
    # CROSS-ENCODER RERANKING
    # ========================================================

    def rerank(
        self,
        query,
        candidates,
        top_k=RERANK_TOP_K
    ):

        if not candidates:
            return []

        pairs = [
            (
                query,
                item.get(
                    "text",
                    ""
                )
            )
            for item in candidates
        ]

        scores = self.reranker.predict(
            pairs
        )

        for item, score in zip(
            candidates,
            scores
        ):

            item["rerank_score"] = float(
                score
            )

        return candidates


    # ========================================================
    # FEATURE-AWARE FINAL SCORING
    # ========================================================

    def score_candidates(
        self,
        candidates,
        existence_question=False,
        detected_features=None
    ):

        detected_features = (
            detected_features or []
        )

        for item in candidates:

            vector_score = item.get(
                "vector_score",
                0.0
            )

            keyword_score = item.get(
                "keyword_score",
                0.0
            )

            rerank_score = item.get(
                "rerank_score",
                0.0
            )

            direct_match = item.get(
                "direct_match",
                False
            )

            text = self.normalize_text(
                item.get(
                    "text",
                    ""
                )
            )

            # ------------------------------------------------
            # Base score
            # ------------------------------------------------

            final_score = (
                rerank_score
                + (vector_score * 1.0)
                + (keyword_score * 1.5)
            )

            # ------------------------------------------------
            # Direct feature evidence
            # ------------------------------------------------

            if direct_match:

                final_score += 4.0

            # ------------------------------------------------
            # Feature-specific matching
            # ------------------------------------------------

            feature_matches = 0

            for feature in detected_features:

                aliases = QUERY_ALIASES.get(
                    feature,
                    []
                )

                for alias in aliases:

                    alias = self.normalize_text(
                        alias
                    )

                    if (
                        alias
                        and alias in text
                    ):

                        feature_matches += 1

                        break

            if feature_matches:

                final_score += (
                    feature_matches * 2.0
                )

            # ------------------------------------------------
            # Existence question
            #
            # For:
            #
            # "Does it have a sunroof?"
            #
            # direct evidence matters much more.
            # ------------------------------------------------

            if existence_question:

                if direct_match:

                    final_score += 3.0

                else:

                    # Semantic-only matches should not
                    # dominate a feature existence question.
                    final_score -= 1.0

            item["feature_matches"] = (
                feature_matches
            )

            item["final_score"] = (
                final_score
            )

        # ----------------------------------------------------
        # Sort
        # ----------------------------------------------------

        candidates.sort(
            key=lambda x: x.get(
                "final_score",
                -999
            ),
            reverse=True
        )

        return candidates


    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    def remove_duplicates(
        self,
        results
    ):

        unique = []

        seen = set()

        for item in results:

            text = self.normalize_text(
                item.get(
                    "text",
                    ""
                )
            )

            if not text:
                continue

            if text in seen:
                continue

            seen.add(
                text
            )

            unique.append(
                item
            )

        return unique


    # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        query,
        brand,
        model,
        top_k=FINAL_TOP_K
    ):

        # ====================================================
        # 1. VEHICLE FILTER
        # ====================================================

        allowed_indices = (
            self.filter_metadata(
                brand=brand,
                model=model
            )
        )

        if not allowed_indices:

            print(
                f"\nNo chunks found for "
                f"{brand} {model}"
            )

            return []


        # ====================================================
        # 2. QUESTION ANALYSIS
        # ====================================================

        detected_features = (
            self.detect_features(
                query
            )
        )

        existence_question = (
            self.is_existence_question(
                query
            )
        )


        # ====================================================
        # 3. KEYWORD SEARCH
        # ====================================================

        keyword_results = (
            self.keyword_search(
                query=query,
                allowed_indices=allowed_indices,
                top_k=KEYWORD_TOP_K
            )
        )


        # ====================================================
        # 4. SEMANTIC SEARCH
        # ====================================================

        vector_results = (
            self.vector_search(
                query=query,
                allowed_indices=allowed_indices,
                top_k=VECTOR_TOP_K
            )
        )


        # ====================================================
        # 5. MERGE
        # ====================================================

        candidates = (
            self.merge_candidates(
                vector_results=vector_results,
                keyword_results=keyword_results
            )
        )


        # ====================================================
        # 6. FALLBACK
        #
        # If a feature isn't explicitly present, we still
        # want contextual chunks from the selected vehicle.
        #
        # But we DON'T pretend these are direct evidence.
        # ====================================================

        if not candidates:

            # Use the first few chunks belonging to
            # the selected vehicle.
            for index in allowed_indices[:10]:

                item = self.metadata[
                    index
                ].copy()

                item["_index"] = index

                item["vector_score"] = 0.0

                item["keyword_score"] = 0.0

                item["direct_match"] = False

                item["matched_keywords"] = []

                candidates.append(
                    item
                )


        # ====================================================
        # 7. LIMIT BEFORE CROSS-ENCODER
        #
        # CrossEncoder is relatively expensive.
        # Keep candidate pool manageable.
        # ====================================================

        candidates.sort(
            key=lambda x: (
                x.get(
                    "direct_match",
                    False
                ),
                x.get(
                    "keyword_score",
                    0.0
                ),
                x.get(
                    "vector_score",
                    0.0
                )
            ),
            reverse=True
        )

        candidates = candidates[
            :RERANK_TOP_K
        ]


        # ====================================================
        # 8. CROSS-ENCODER
        # ====================================================

        candidates = (
            self.rerank(
                query=query,
                candidates=candidates,
                top_k=RERANK_TOP_K
            )
        )


        # ====================================================
        # 9. FINAL FEATURE-AWARE SCORING
        # ====================================================

        candidates = (
            self.score_candidates(
                candidates=candidates,
                existence_question=(
                    existence_question
                ),
                detected_features=(
                    detected_features
                )
            )
        )


        # ====================================================
        # 10. REMOVE DUPLICATES
        # ====================================================

        candidates = (
            self.remove_duplicates(
                candidates
            )
        )


        # ====================================================
        # 11. FINAL RESULTS
        # ====================================================

        results = candidates[:top_k]


        # ====================================================
        # 12. ATTACH RETRIEVAL INFORMATION
        # ====================================================

        has_direct_evidence = any(
            item.get(
                "direct_match",
                False
            )
            for item in results
        )

        for item in results:

            item["query_features"] = (
                detected_features
            )

            item["existence_question"] = (
                existence_question
            )

            item["has_direct_evidence"] = (
                has_direct_evidence
            )

        return results


# ============================================================
# TEST FUNCTION
# ============================================================

def main():

    print(
        "\n" + "=" * 65
    )

    print(
        "DRIVE WISE - HYBRID RETRIEVAL TEST"
    )

    print(
        "=" * 65
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
    # Continuous testing
    # --------------------------------------------------------

    while True:

        query = input(
            "\nEnter question "
            "(type 'exit' to stop): "
        ).strip()

        if query.lower() in {
            "exit",
            "quit"
        }:

            print(
                "\nExiting."
            )

            break

        if not query:

            continue

        print(
            "\nSearching..."
        )

        results = retriever.search(
            query=query,
            brand=brand,
            model=model,
            top_k=FINAL_TOP_K
        )

        print(
            "\n" + "=" * 65
        )

        print(
            f"Retrieved {len(results)} chunks"
        )

        print(
            "=" * 65
        )

        if not results:

            print(
                "\nNo brochure information found."
            )

            continue

        for number, result in enumerate(
            results,
            start=1
        ):

            print(
                f"\nRESULT {number}"
            )

            print(
                "-" * 65
            )

            print(
                f"Brand       : "
                f"{result.get('brand', '')}"
            )

            print(
                f"Model       : "
                f"{result.get('model', '')}"
            )

            print(
                f"Section     : "
                f"{result.get('section', '')}"
            )

            print(
                f"Page        : "
                f"{result.get('page', '')}"
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
                f"Rerank      : "
                f"{result.get('rerank_score', 0):.4f}"
            )

            print(
                f"Final       : "
                f"{result.get('final_score', 0):.4f}"
            )

            print(
                f"Direct      : "
                f"{result.get('direct_match', False)}"
            )

            print(
                f"Features    : "
                f"{result.get('query_features', [])}"
            )

            print(
                f"Matched     : "
                f"{result.get('matched_keywords', [])}"
            )

            print(
                "\nText:"
            )

            print(
                result.get(
                    "text",
                    ""
                )
            )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()