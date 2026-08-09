import json
import re
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


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


# ============================================================
# RETRIEVAL SETTINGS
# ============================================================

VECTOR_TOP_K = 30
KEYWORD_TOP_K = 30

MIN_VECTOR_SCORE = 0.15


# ============================================================
# QUERY ALIASES
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
# RETRIEVER
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


    # ========================================================
    # NORMALIZE TEXT
    # ========================================================

    @staticmethod
    def normalize_text(text):

        if text is None:
            return ""

        text = str(text).lower()

        text = text.replace("-", " ")

        text = text.replace("_", " ")

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

        text = self.normalize_text(text)

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

            "mahindra",
            "thar",
            "xuv3xo",
            "scorpio"
        }

        return [
            token
            for token in tokens
            if token not in stop_words
        ]


    # ========================================================
    # FILTER BY VEHICLE
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

                allowed_indices.append(index)

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

                detected.append(feature)

                continue

            for alias in aliases:

                alias_text = self.normalize_text(
                    alias
                )

                if alias_text in normalized_query:

                    detected.append(feature)

                    break

        return list(
            dict.fromkeys(detected)
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

        expanded = [
            normalized_query
        ]

        detected_features = self.detect_features(
            query
        )

        for feature in detected_features:

            aliases = QUERY_ALIASES.get(
                feature,
                []
            )

            expanded.extend(
                aliases
            )

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

            final_queries.append(item)

        return final_queries


    # ========================================================
    # KEYWORD SEARCH
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

            score = 0.0

            if query_tokens:

                coverage = (
                    len(matched_tokens)
                    / len(query_tokens)
                )

                score += coverage * 2.0

            score += (
                len(set(matched_aliases)) * 2.5
            )

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

            result["direct_match"] = (
                len(matched_aliases) > 0
            )

            results.append(result)

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

        embedding = (
            self.embedding_model.encode(
                [query],
                convert_to_numpy=True
            )
        )

        embedding = embedding.astype(
            "float32"
        )

        faiss.normalize_L2(
            embedding
        )

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

            score = float(score)

            if score < MIN_VECTOR_SCORE:
                continue

            item = self.metadata[
                index
            ].copy()

            item["_index"] = index

            item["vector_score"] = score

            results.append(item)

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
        # Vector results
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
        # Keyword results
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

            seen.add(text)

            unique.append(item)

        return unique


    # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        query,
        brand,
        model,
        top_k=30
    ):

        print("\n" + "-" * 70)
        print("HYBRID RETRIEVAL")
        print("-" * 70)

        print(
            f"Brand : {brand}"
        )

        print(
            f"Model : {model}"
        )

        print(
            f"Query : {query}"
        )

        # ----------------------------------------------------
        # 1. Vehicle filtering
        # ----------------------------------------------------

        allowed_indices = self.filter_metadata(
            brand=brand,
            model=model
        )

        print(
            f"\nVehicle chunks available: "
            f"{len(allowed_indices)}"
        )

        if not allowed_indices:

            print(
                "❌ No chunks found for vehicle."
            )

            return []

        # ----------------------------------------------------
        # 2. Keyword search
        # ----------------------------------------------------

        keyword_results = self.keyword_search(
            query=query,
            allowed_indices=allowed_indices,
            top_k=KEYWORD_TOP_K
        )

        print(
            f"✓ Keyword candidates: "
            f"{len(keyword_results)}"
        )

        # ----------------------------------------------------
        # 3. Vector search
        # ----------------------------------------------------

        vector_results = self.vector_search(
            query=query,
            allowed_indices=allowed_indices,
            top_k=VECTOR_TOP_K
        )

        print(
            f"✓ Vector candidates: "
            f"{len(vector_results)}"
        )

        # ----------------------------------------------------
        # 4. Merge
        # ----------------------------------------------------

        candidates = self.merge_candidates(
            vector_results=vector_results,
            keyword_results=keyword_results
        )

        # ----------------------------------------------------
        # 5. Fallback
        # ----------------------------------------------------

        if not candidates:

            print(
                "⚠ No keyword/vector candidates."
            )

            for index in allowed_indices[:10]:

                item = self.metadata[
                    index
                ].copy()

                item["_index"] = index

                item["vector_score"] = 0.0

                item["keyword_score"] = 0.0

                item["matched_keywords"] = []

                item["direct_match"] = False

                candidates.append(item)

        # ----------------------------------------------------
        # 6. Remove duplicate chunks
        # ----------------------------------------------------

        candidates = self.remove_duplicates(
            candidates
        )

        # ----------------------------------------------------
        # 7. Sort retrieval candidates
        #
        # IMPORTANT:
        # This is NOT CrossEncoder reranking.
        # The separate Reranker handles that.
        # ----------------------------------------------------

        candidates.sort(
            key=lambda item: (
                item.get(
                    "direct_match",
                    False
                ),
                item.get(
                    "keyword_score",
                    0.0
                ),
                item.get(
                    "vector_score",
                    0.0
                )
            ),
            reverse=True
        )

        results = candidates[:top_k]

        print(
            f"✓ Final retrieval candidates: "
            f"{len(results)}"
        )

        return results


# ============================================================
# TEST
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("DRIVE WISE - RETRIEVER TEST")
    print("=" * 70)

    retriever = HybridRetriever()

    brand = "mahindra"
    model = "xuv3xo"

    query = (
        "What is the maximum power "
        "of the XUV 3XO?"
    )

    results = retriever.search(
        query=query,
        brand=brand,
        model=model,
        top_k=10
    )

    print("\n" + "=" * 70)
    print("RETRIEVAL RESULTS")
    print("=" * 70)

    for number, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\nResult {number}"
        )

        print("-" * 70)

        print(
            f"Index   : "
            f"{result.get('_index')}"
        )

        print(
            f"Section : "
            f"{result.get('section', '')}"
        )

        print(
            f"Page    : "
            f"{result.get('page', '')}"
        )

        print(
            f"Vector  : "
            f"{result.get('vector_score', 0):.4f}"
        )

        print(
            f"Keyword : "
            f"{result.get('keyword_score', 0):.4f}"
        )

        print(
            f"Direct  : "
            f"{result.get('direct_match', False)}"
        )

        print(
            f"Matched : "
            f"{result.get('matched_keywords', [])}"
        )

        print(
            f"Text    : "
            f"{result.get('text', '')}"
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()