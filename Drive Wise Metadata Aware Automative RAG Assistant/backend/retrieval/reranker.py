import re

from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(
        self,
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        print("\nLoading re-ranking model...")

        self.model_name = model_name

        self.model = CrossEncoder(
            model_name
        )

        print(
            f"✓ Re-ranking model loaded: "
            f"{model_name}"
        )

    # ============================================================
    # TEXT NORMALIZATION
    # ============================================================

    def normalize_text(self, text):

        text = str(text).lower()

        text = text.replace("-", " ")
        text = text.replace("/", " ")
        text = text.replace("@", " ")

        text = re.sub(
            r"[^a-z0-9\s]",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # ============================================================
    # QUERY TYPE DETECTION
    # ============================================================

    def detect_query_type(self, query):

        q = self.normalize_text(query)

        technical_terms = {

            "power": [
                "power",
                "maximum power",
                "horsepower",
                "bhp",
                "kw",
                "ps"
            ],

            "torque": [
                "torque",
                "maximum torque",
                "nm"
            ],

            "engine": [
                "engine",
                "engine type",
                "engine capacity",
                "displacement"
            ],

            "mileage": [
                "mileage",
                "fuel efficiency",
                "efficiency"
            ],

            "transmission": [
                "transmission",
                "gearbox",
                "automatic",
                "manual"
            ],

            "dimensions": [
                "length",
                "width",
                "height",
                "wheelbase",
                "ground clearance",
                "dimensions"
            ],

            "safety": [
                "airbag",
                "abs",
                "esc",
                "safety",
                "adas"
            ],

            "fuel": [
                "fuel",
                "petrol",
                "diesel",
                "fuel tank"
            ],

            "seating": [
                "seat",
                "seating",
                "seating capacity"
            ]
        }

        for query_type, terms in technical_terms.items():

            for term in terms:

                if term in q:

                    return query_type

        return "general"

    # ============================================================
    # TECHNICAL EVIDENCE SCORE
    # ============================================================

    def technical_evidence_score(
        self,
        query,
        text,
        section=""
    ):

        q = self.normalize_text(query)
        t = self.normalize_text(text)
        s = self.normalize_text(section)

        query_type = self.detect_query_type(
            query
        )

        score = 0.0

        # --------------------------------------------------------
        # POWER
        # --------------------------------------------------------

        if query_type == "power":

            # Exact phrase
            if "maximum power" in t:
                score += 6.0

            elif "max power" in t:
                score += 5.0

            elif "power" in t:
                score += 2.0

            # Power units
            if re.search(
                r"\b\d+(?:\.\d+)?\s*kw\b",
                t
            ):
                score += 4.0

            if re.search(
                r"\b\d+(?:\.\d+)?\s*ps\b",
                t
            ):
                score += 4.0

            if re.search(
                r"\b\d+(?:\.\d+)?\s*bhp\b",
                t
            ):
                score += 4.0

            # RPM
            if "rpm" in t or "r min" in t:
                score += 2.0

            # Relevant section
            if (
                "engine" in s
                or "specification" in s
                or "performance" in s
            ):
                score += 4.0

        # --------------------------------------------------------
        # TORQUE
        # --------------------------------------------------------

        elif query_type == "torque":

            if "maximum torque" in t:
                score += 6.0

            elif "max torque" in t:
                score += 5.0

            elif "torque" in t:
                score += 2.0

            if re.search(
                r"\b\d+(?:\.\d+)?\s*nm\b",
                t
            ):
                score += 5.0

            if (
                "engine" in s
                or "specification" in s
                or "performance" in s
            ):
                score += 4.0

        # --------------------------------------------------------
        # ENGINE
        # --------------------------------------------------------

        elif query_type == "engine":

            if "engine type" in t:
                score += 6.0

            if "engine" in t:
                score += 2.0

            if (
                "engine" in s
                or "specification" in s
                or "performance" in s
            ):
                score += 4.0

        # --------------------------------------------------------
        # TRANSMISSION
        # --------------------------------------------------------

        elif query_type == "transmission":

            if "transmission type" in t:
                score += 6.0

            if "transmission" in t:
                score += 3.0

            if (
                "engine" in s
                or "specification" in s
            ):
                score += 3.0

        # --------------------------------------------------------
        # DIMENSIONS
        # --------------------------------------------------------

        elif query_type == "dimensions":

            dimension_terms = [
                "length",
                "width",
                "height",
                "wheelbase",
                "ground clearance",
                "turning radius"
            ]

            for term in dimension_terms:

                if term in q and term in t:
                    score += 5.0

            if "dimension" in s:
                score += 5.0

        # --------------------------------------------------------
        # SAFETY
        # --------------------------------------------------------

        elif query_type == "safety":

            if "safety" in t:
                score += 3.0

            if "airbag" in t:
                score += 3.0

            if "adas" in t:
                score += 3.0

            if "safety" in s:
                score += 4.0

        # --------------------------------------------------------
        # GENERAL
        # --------------------------------------------------------

        else:

            query_words = set(
                q.split()
            )

            text_words = set(
                t.split()
            )

            overlap = (
                len(query_words & text_words)
                /
                max(len(query_words), 1)
            )

            score += overlap * 5.0

        return score

    # ============================================================
    # TERM OVERLAP
    # ============================================================

    def term_overlap(
        self,
        query,
        text
    ):

        q_words = set(
            self.normalize_text(query).split()
        )

        t_words = set(
            self.normalize_text(text).split()
        )

        if not q_words:
            return 0.0

        return (
            len(q_words & t_words)
            /
            len(q_words)
        )

    # ============================================================
    # NORMALIZE SCORE
    # ============================================================

    def normalize_score(
        self,
        score,
        minimum,
        maximum
    ):

        if maximum == minimum:
            return 0.5

        return (
            (score - minimum)
            /
            (maximum - minimum)
        )

    # ============================================================
    # RERANK
    # ============================================================

    def rerank(
        self,
        query,
        candidates,
        top_k=5
    ):

        if not candidates:
            return []

        pairs = []

        valid_candidates = []

        for candidate in candidates:

            text = str(
                candidate.get(
                    "text",
                    ""
                )
            ).strip()

            if not text:
                continue

            pairs.append(
                (
                    query,
                    text
                )
            )

            valid_candidates.append(
                candidate.copy()
            )

        if not pairs:
            return []

        print(
            f"\nRe-ranking {len(pairs)} candidates..."
        )

        # --------------------------------------------------------
        # CROSS ENCODER
        # --------------------------------------------------------

        cross_scores = self.model.predict(
            pairs
        )

        # --------------------------------------------------------
        # CALCULATE ALL SCORES
        # --------------------------------------------------------

        results = []

        for candidate, cross_score in zip(
            valid_candidates,
            cross_scores
        ):

            text = candidate.get(
                "text",
                ""
            )

            section = candidate.get(
                "section",
                ""
            )

            keyword_score = float(
                candidate.get(
                    "keyword_score",
                    0.0
                )
            )

            overlap = self.term_overlap(
                query,
                text
            )

            technical_score = (
                self.technical_evidence_score(
                    query=query,
                    text=text,
                    section=section
                )
            )

            candidate["cross_encoder_score"] = float(
                cross_score
            )

            candidate["term_overlap"] = float(
                overlap
            )

            candidate["technical_evidence_score"] = float(
                technical_score
            )

            results.append(
                candidate
            )

        # ========================================================
        # NORMALIZE CROSS ENCODER
        # ========================================================

        cross_values = [
            r["cross_encoder_score"]
            for r in results
        ]

        cross_min = min(
            cross_values
        )

        cross_max = max(
            cross_values
        )

        # ========================================================
        # NORMALIZE KEYWORD SCORE
        # ========================================================

        keyword_values = [
            float(
                r.get(
                    "keyword_score",
                    0.0
                )
            )
            for r in results
        ]

        keyword_min = min(
            keyword_values
        )

        keyword_max = max(
            keyword_values
        )

        # ========================================================
        # NORMALIZE TECHNICAL SCORE
        # ========================================================

        technical_values = [
            r["technical_evidence_score"]
            for r in results
        ]

        technical_min = min(
            technical_values
        )

        technical_max = max(
            technical_values
        )

        # ========================================================
        # FINAL SCORE
        # ========================================================

        for candidate in results:

            cross_norm = self.normalize_score(
                candidate["cross_encoder_score"],
                cross_min,
                cross_max
            )

            keyword_norm = self.normalize_score(
                float(
                    candidate.get(
                        "keyword_score",
                        0.0
                    )
                ),
                keyword_min,
                keyword_max
            )

            technical_norm = self.normalize_score(
                candidate["technical_evidence_score"],
                technical_min,
                technical_max
            )

            overlap = candidate[
                "term_overlap"
            ]

            # ----------------------------------------------------
            # IMPORTANT:
            #
            # Technical evidence gets the highest weight.
            # This is important for brochure specifications.
            # ----------------------------------------------------

            final_score = (
                0.50 * technical_norm
                +
                0.20 * cross_norm
                +
                0.20 * keyword_norm
                +
                0.10 * overlap
            )

            candidate[
                "final_score"
            ] = float(
                final_score
            )

        # ========================================================
        # SORT
        # ========================================================

        results.sort(
            key=lambda item: item.get(
                "final_score",
                0.0
            ),
            reverse=True
        )

        # ========================================================
        # DISPLAY RANKING
        # ========================================================

        print(
            "\n## FINAL RERANK SCORES"
        )

        for rank, result in enumerate(
            results,
            start=1
        ):

            print(
                f"\nRank {rank}"
            )

            print(
                f"Page           : "
                f"{result.get('page', '')}"
            )

            print(
                f"Section        : "
                f"{result.get('section', '')}"
            )

            print(
                f"Keyword Score  : "
                f"{result.get('keyword_score', 0):.4f}"
            )

            print(
                f"CrossEncoder   : "
                f"{result.get('cross_encoder_score', 0):.4f}"
            )

            print(
                f"Technical      : "
                f"{result.get('technical_evidence_score', 0):.4f}"
            )

            print(
                f"Term Overlap   : "
                f"{result.get('term_overlap', 0):.4f}"
            )

            print(
                f"Final Score    : "
                f"{result.get('final_score', 0):.4f}"
            )

        return results[:top_k]


# ============================================================
# TEST
# ============================================================

def main():

    print(
        "\n" + "=" * 70
    )

    print(
        "DRIVE WISE - RE-RANKER TEST"
    )

    print(
        "=" * 70
    )

    reranker = Reranker()

    query = (
        "What is the maximum power "
        "of the XUV 3XO?"
    )

    candidates = [

        {
            "brand": "mahindra",
            "model": "xuv3xo",
            "section": "Engine",
            "page": 12,
            "keyword_score": 4.0,
            "text": (
                "The XUV 3XO is equipped "
                "with powerful engine options."
            )
        },

        {
            "brand": "mahindra",
            "model": "xuv3xo",
            "section": "Engine Specifications",
            "page": 13,
            "keyword_score": 8.0,
            "text": (
                "The maximum power output "
                "is 130 PS."
            )
        },

        {
            "brand": "mahindra",
            "model": "xuv3xo",
            "section": "Safety",
            "page": 20,
            "keyword_score": 2.0,
            "text": (
                "The vehicle is equipped "
                "with multiple airbags and "
                "safety features."
            )
        },

        {
            "brand": "mahindra",
            "model": "xuv3xo",
            "section": "Interior",
            "page": 25,
            "keyword_score": 1.0,
            "text": (
                "The cabin provides comfortable "
                "seating and premium materials."
            )
        }
    ]

    results = reranker.rerank(
        query=query,
        candidates=candidates,
        top_k=3
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "RERANKED RESULTS"
    )

    print(
        "=" * 70
    )

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
            f"Section        : "
            f"{result.get('section', '')}"
        )

        print(
            f"Page           : "
            f"{result.get('page', '')}"
        )

        print(
            f"Keyword Score  : "
            f"{result.get('keyword_score', 0):.4f}"
        )

        print(
            f"CrossEncoder   : "
            f"{result.get('cross_encoder_score', 0):.4f}"
        )

        print(
            f"Technical      : "
            f"{result.get('technical_evidence_score', 0):.4f}"
        )

        print(
            f"Term Overlap   : "
            f"{result.get('term_overlap', 0):.4f}"
        )

        print(
            f"Final Score    : "
            f"{result.get('final_score', 0):.4f}"
        )

        print(
            f"Text           : "
            f"{result.get('text', '')}"
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()