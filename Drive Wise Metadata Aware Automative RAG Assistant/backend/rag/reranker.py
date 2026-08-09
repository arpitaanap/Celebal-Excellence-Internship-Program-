import re
import math
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

    def _normalize(self, text):
        """
        Normalize text for keyword and technical matching.
        """

        text = str(text).lower()

        # Normalize common OCR variations
        text = text.replace("max.", "max")
        text = text.replace("maximum", "maximum")

        # Normalize @ spacing
        text = re.sub(
            r"\s*@\s*",
            " @ ",
            text
        )

        # Normalize slash spacing
        text = re.sub(
            r"\s*/\s*",
            "/",
            text
        )

        # Keep useful technical characters
        text = re.sub(
            r"[^a-z0-9.%@+\-\/ ]",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        return text

    # ============================================================
    # QUERY TYPE DETECTION
    # ============================================================

    def _detect_query_type(self, query):
        """
        Detect the type of technical question.
        """

        query = self._normalize(query)

        technical_patterns = {

            "power": [
                "maximum power",
                "max power",
                "power output",
                "horsepower",
                "bhp",
                "kw",
                "ps"
            ],

            "torque": [
                "maximum torque",
                "max torque",
                "torque",
                "nm"
            ],

            "mileage": [
                "mileage",
                "fuel efficiency",
                "fuel economy",
                "kmpl",
                "km/l"
            ],

            "engine": [
                "engine",
                "engine type",
                "engine capacity",
                "engine displacement",
                "displacement"
            ],

            "transmission": [
                "transmission",
                "gearbox",
                "automatic",
                "manual",
                "amt",
                "dct",
                "cvt"
            ],

            "dimensions": [
                "length",
                "width",
                "height",
                "wheelbase",
                "ground clearance",
                "turning radius",
                "dimensions"
            ],

            "fuel": [
                "fuel type",
                "fuel tank",
                "tank capacity",
                "petrol",
                "diesel",
                "fuel"
            ],

            "safety": [
                "airbag",
                "airbags",
                "abs",
                "esc",
                "esp",
                "safety",
                "brake",
                "isofix"
            ]
        }

        detected = []

        for query_type, patterns in technical_patterns.items():

            for pattern in patterns:

                if pattern in query:

                    detected.append(
                        query_type
                    )

                    break

        return detected

    # ============================================================
    # PHRASE GROUPS
    # ============================================================

    def _get_phrase_groups(self):
        """
        Related phrases representing the same concept.
        """

        return {

            "maximum_power": [
                "maximum power",
                "max power",
                "power output",
                "peak power",
                "horsepower",
                "bhp"
            ],

            "maximum_torque": [
                "maximum torque",
                "max torque",
                "peak torque",
                "torque"
            ],

            "fuel_efficiency": [
                "fuel efficiency",
                "fuel economy",
                "mileage",
                "kmpl",
                "km/l"
            ],

            "engine_type": [
                "engine type",
                "engine",
                "powertrain"
            ],

            "engine_capacity": [
                "engine capacity",
                "engine displacement",
                "displacement",
                "capacity"
            ],

            "transmission": [
                "transmission",
                "transmission type",
                "gearbox",
                "automatic",
                "manual",
                "amt",
                "dct",
                "cvt"
            ],

            "ground_clearance": [
                "ground clearance"
            ],

            "turning_radius": [
                "turning radius"
            ],

            "wheelbase": [
                "wheelbase"
            ],

            "fuel_tank": [
                "fuel tank",
                "tank capacity"
            ],

            "safety": [
                "safety",
                "airbag",
                "airbags",
                "abs",
                "esc",
                "esp",
                "isofix"
            ]
        }

    # ============================================================
    # PHRASE GROUP MATCHING
    # ============================================================

    def _phrase_group_match(
        self,
        query,
        text,
        phrases
    ):
        """
        Check whether query and text contain equivalent
        phrases from the same semantic group.
        """

        query_normalized = self._normalize(
            query
        )

        text_normalized = self._normalize(
            text
        )

        query_match = any(
            phrase in query_normalized
            for phrase in phrases
        )

        text_match = any(
            phrase in text_normalized
            for phrase in phrases
        )

        return (
            query_match
            and
            text_match
        )

    # ============================================================
    # TECHNICAL EVIDENCE SCORE
    # ============================================================

    def _technical_score(
        self,
        query,
        text,
        section=""
    ):
        """
        Calculate domain-specific technical evidence.

        Strongly rewards explicit brochure specifications
        rather than generic marketing language.
        """

        query_normalized = self._normalize(
            query
        )

        text_normalized = self._normalize(
            text
        )

        section_normalized = self._normalize(
            section
        )

        score = 0.0

        query_types = self._detect_query_type(
            query
        )

        phrase_groups = self._get_phrase_groups()

        # ========================================================
        # POWER
        # ========================================================

        if "power" in query_types:

            # Query asks specifically for maximum power
            if (
                "maximum power"
                in query_normalized
            ):
                score += 3.0

            if (
                "max power"
                in query_normalized
            ):
                score += 3.0

            # Equivalent phrase in document
            if self._phrase_group_match(
                query,
                text,
                phrase_groups[
                    "maximum_power"
                ]
            ):
                score += 5.0

            # Explicit max power label
            if (
                "max power"
                in text_normalized
            ):
                score += 5.0

            if (
                "maximum power"
                in text_normalized
            ):
                score += 5.0

            # kW value
            kw_matches = re.findall(
                r"\b\d+(?:\.\d+)?\s*kw\b",
                text_normalized
            )

            if kw_matches:
                score += 4.0

            # PS value
            ps_matches = re.findall(
                r"\b\d+(?:\.\d+)?\s*ps\b",
                text_normalized
            )

            if ps_matches:
                score += 4.0

            # BHP value
            bhp_matches = re.findall(
                r"\b\d+(?:\.\d+)?\s*bhp\b",
                text_normalized
            )

            if bhp_matches:
                score += 4.0

            # Power + RPM
            if re.search(
                r"\b\d+(?:\.\d+)?\s*kw\s*@\s*\d+",
                text_normalized
            ):
                score += 5.0

            if re.search(
                r"\b\d+(?:\.\d+)?\s*(?:ps|bhp)\s*@\s*\d+",
                text_normalized
            ):
                score += 4.0

            # Engine/performance section
            if (
                "engine" in section_normalized
                or
                "performance" in section_normalized
                or
                "specification" in section_normalized
                or
                "technical" in section_normalized
            ):
                score += 2.0

            # Strong phrase
            if "power of" in text_normalized:
                score += 3.0

        # ========================================================
        # TORQUE
        # ========================================================

        if "torque" in query_types:

            if self._phrase_group_match(
                query,
                text,
                phrase_groups[
                    "maximum_torque"
                ]
            ):
                score += 5.0

            if "max torque" in text_normalized:
                score += 5.0

            if "maximum torque" in text_normalized:
                score += 5.0

            # Nm value
            if re.search(
                r"\b\d+(?:\.\d+)?\s*nm\b",
                text_normalized
            ):
                score += 5.0

            # Torque + RPM
            if re.search(
                r"\b\d+(?:\.\d+)?\s*nm\s*@\s*\d+",
                text_normalized
            ):
                score += 4.0

            if (
                "engine" in section_normalized
                or
                "performance" in section_normalized
                or
                "technical" in section_normalized
            ):
                score += 2.0

        # ========================================================
        # MILEAGE
        # ========================================================

        if "mileage" in query_types:

            if self._phrase_group_match(
                query,
                text,
                phrase_groups[
                    "fuel_efficiency"
                ]
            ):
                score += 5.0

            if "mileage" in text_normalized:
                score += 5.0

            if "fuel efficiency" in text_normalized:
                score += 5.0

            if "fuel economy" in text_normalized:
                score += 5.0

            if "kmpl" in text_normalized:
                score += 5.0

            if "km/l" in text_normalized:
                score += 5.0

        # ========================================================
        # ENGINE
        # ========================================================

        if "engine" in query_types:

            if "engine type" in text_normalized:
                score += 5.0

            if (
                "engine capacity"
                in text_normalized
            ):
                score += 5.0

            if (
                "engine displacement"
                in text_normalized
            ):
                score += 5.0

            if re.search(
                r"\b\d+(?:\.\d+)?\s*l\b",
                text_normalized
            ):
                score += 3.0

            if "engine" in section_normalized:
                score += 2.0

        # ========================================================
        # TRANSMISSION
        # ========================================================

        if "transmission" in query_types:

            if (
                "transmission type"
                in text_normalized
            ):
                score += 5.0

            if "transmission" in text_normalized:
                score += 3.0

            if "gearbox" in text_normalized:
                score += 3.0

            if "6 mt" in text_normalized:
                score += 2.0

            if "6 at" in text_normalized:
                score += 2.0

            if "automatic" in text_normalized:
                score += 2.0

            if "manual" in text_normalized:
                score += 2.0

        # ========================================================
        # DIMENSIONS
        # ========================================================

        if "dimensions" in query_types:

            dimension_terms = [
                "length",
                "width",
                "height",
                "wheelbase",
                "ground clearance",
                "turning radius"
            ]

            for term in dimension_terms:

                if term in query_normalized:

                    if term in text_normalized:
                        score += 5.0

            if "dimensions" in text_normalized:
                score += 3.0

            if "dimensions" in section_normalized:
                score += 2.0

        # ========================================================
        # FUEL
        # ========================================================

        if "fuel" in query_types:

            if "fuel type" in text_normalized:
                score += 5.0

            if "fuel tank" in text_normalized:
                score += 5.0

            if "tank capacity" in text_normalized:
                score += 5.0

            if "petrol" in text_normalized:
                score += 2.0

            if "diesel" in text_normalized:
                score += 2.0

        # ========================================================
        # SAFETY
        # ========================================================

        if "safety" in query_types:

            safety_terms = [
                "airbag",
                "airbags",
                "abs",
                "esc",
                "esp",
                "safety",
                "brake",
                "isofix"
            ]

            for term in safety_terms:

                if term in text_normalized:
                    score += 3.0

            if "safety" in section_normalized:
                score += 3.0

        return score

    # ============================================================
    # TECHNICAL EVIDENCE VALIDATION
    # ============================================================

    def _is_relevant_evidence(
        self,
        query,
        text
    ):
        """
        Prevent obviously irrelevant chunks from entering
        final evidence selection.

        This is query-type specific.
        """

        text_normalized = self._normalize(
            text
        )

        query_types = self._detect_query_type(
            query
        )

        # ========================================================
        # POWER
        # ========================================================

        if "power" in query_types:

            has_power_label = (
                "max power"
                in text_normalized
                or
                "maximum power"
                in text_normalized
                or
                "power output"
                in text_normalized
            )

            has_power_value = bool(
                re.search(
                    r"\b\d+(?:\.\d+)?\s*kw\s*@\s*\d+",
                    text_normalized
                )
            )

            has_ps_value = bool(
                re.search(
                    r"\b\d+(?:\.\d+)?\s*ps\b",
                    text_normalized
                )
            )

            has_bhp_value = bool(
                re.search(
                    r"\b\d+(?:\.\d+)?\s*bhp\b",
                    text_normalized
                )
            )

            return (
                has_power_label
                or
                has_power_value
                or
                has_ps_value
                or
                has_bhp_value
            )

        # ========================================================
        # TORQUE
        # ========================================================

        if "torque" in query_types:

            return bool(
                re.search(
                    r"\b\d+(?:\.\d+)?\s*nm\b",
                    text_normalized
                )
            ) or (
                "max torque"
                in text_normalized
                or
                "maximum torque"
                in text_normalized
            )

        # ========================================================
        # MILEAGE
        # ========================================================

        if "mileage" in query_types:

            return (
                "mileage" in text_normalized
                or
                "fuel efficiency" in text_normalized
                or
                "fuel economy" in text_normalized
                or
                "kmpl" in text_normalized
                or
                "km/l" in text_normalized
            )

        # ========================================================
        # ENGINE
        # ========================================================

        if "engine" in query_types:

            return (
                "engine" in text_normalized
                or
                "engine type" in text_normalized
                or
                "capacity" in text_normalized
                or
                "displacement" in text_normalized
            )

        # ========================================================
        # TRANSMISSION
        # ========================================================

        if "transmission" in query_types:

            return (
                "transmission" in text_normalized
                or
                "gearbox" in text_normalized
                or
                "automatic" in text_normalized
                or
                "manual" in text_normalized
                or
                "6 mt" in text_normalized
                or
                "6 at" in text_normalized
            )

        # ========================================================
        # DIMENSIONS
        # ========================================================

        if "dimensions" in query_types:

            dimension_terms = [
                "length",
                "width",
                "height",
                "wheelbase",
                "ground clearance",
                "turning radius"
            ]

            return any(
                term in text_normalized
                for term in dimension_terms
            )

        # ========================================================
        # FUEL
        # ========================================================

        if "fuel" in query_types:

            return (
                "fuel" in text_normalized
                or
                "petrol" in text_normalized
                or
                "diesel" in text_normalized
                or
                "tank capacity" in text_normalized
            )

        # ========================================================
        # SAFETY
        # ========================================================

        if "safety" in query_types:

            safety_terms = [
                "airbag",
                "airbags",
                "abs",
                "esc",
                "esp",
                "safety",
                "isofix",
                "brake"
            ]

            return any(
                term in text_normalized
                for term in safety_terms
            )

        # ========================================================
        # GENERAL QUESTION
        # ========================================================

        return True

    # ============================================================
    # TERM OVERLAP
    # ============================================================

    def _term_overlap(
        self,
        query,
        text
    ):
        """
        Calculate meaningful query-term overlap.
        """

        query_words = set(
            self._normalize(
                query
            ).split()
        )

        text_words = set(
            self._normalize(
                text
            ).split()
        )

        if not query_words:
            return 0.0

        stop_words = {
            "what",
            "is",
            "the",
            "of",
            "a",
            "an",
            "how",
            "does",
            "do",
            "for",
            "in",
            "on",
            "with",
            "which",
            "are",
            "was",
            "were",
            "can",
            "could"
        }

        query_words -= stop_words

        if not query_words:
            return 0.0

        overlap = (
            query_words
            .intersection(
                text_words
            )
        )

        return (
            len(overlap)
            /
            len(query_words)
        )

    # ============================================================
    # KEYWORD SCORE
    # ============================================================

    def _keyword_score(
        self,
        query,
        text
    ):
        """
        Calculate direct lexical relevance.

        Uses semantic phrase groups so that:
            maximum power
            max power
            max. power

        are treated as equivalent.
        """

        query_normalized = self._normalize(
            query
        )

        text_normalized = self._normalize(
            text
        )

        score = 0.0

        phrase_groups = self._get_phrase_groups()

        # ========================================================
        # Important phrase groups
        # ========================================================

        important_groups = [
            "maximum_power",
            "maximum_torque",
            "fuel_efficiency",
            "engine_type",
            "engine_capacity",
            "transmission",
            "ground_clearance",
            "turning_radius",
            "wheelbase",
            "fuel_tank",
            "safety"
        ]

        for group_name in important_groups:

            phrases = phrase_groups[
                group_name
            ]

            query_match = any(
                phrase in query_normalized
                for phrase in phrases
            )

            if not query_match:
                continue

            text_match = any(
                phrase in text_normalized
                for phrase in phrases
            )

            if text_match:
                score += 5.0

        # ========================================================
        # Individual query terms
        # ========================================================

        query_words = set(
            query_normalized.split()
        )

        text_words = set(
            text_normalized.split()
        )

        for word in query_words:

            if len(word) <= 2:
                continue

            if word in text_words:
                score += 1.0

        return score

    # ============================================================
    # CROSS ENCODER NORMALIZATION
    # ============================================================

    def _normalize_cross_encoder(
        self,
        score
    ):
        """
        Convert CrossEncoder raw logit to 0-1.

        MS MARCO CrossEncoder produces raw logits.
        """

        try:

            score = float(
                score
            )

            # Prevent overflow
            score = max(
                min(score, 50.0),
                -50.0
            )

            return (
                1.0
                /
                (
                    1.0
                    +
                    math.exp(-score)
                )
            )

        except Exception:

            return 0.0

    # ============================================================
    # TECHNICAL SCORE NORMALIZATION
    # ============================================================

    def _normalize_technical_score(
        self,
        technical_score
    ):
        """
        Smoothly normalize technical evidence.

        Avoids hard saturation at 20.
        """

        technical_score = max(
            float(technical_score),
            0.0
        )

        return (
            technical_score
            /
            (
                technical_score
                +
                10.0
            )
        )

    # ============================================================
    # KEYWORD SCORE NORMALIZATION
    # ============================================================

    def _normalize_keyword_score(
        self,
        keyword_score
    ):
        """
        Smooth keyword normalization.
        """

        keyword_score = max(
            float(keyword_score),
            0.0
        )

        return (
            keyword_score
            /
            (
                keyword_score
                +
                5.0
            )
        )

    # ============================================================
    # FINAL SCORE
    # ============================================================

    def _calculate_final_score(
        self,
        keyword_score,
        cross_encoder_score,
        technical_score,
        term_overlap
    ):
        """
        Combine all ranking signals.

        We intentionally give technical evidence the
        highest weight because automotive brochure
        questions are specification-heavy.
        """

        cross_normalized = (
            self._normalize_cross_encoder(
                cross_encoder_score
            )
        )

        technical_normalized = (
            self._normalize_technical_score(
                technical_score
            )
        )

        keyword_normalized = (
            self._normalize_keyword_score(
                keyword_score
            )
        )

        term_overlap = max(
            min(
                float(term_overlap),
                1.0
            ),
            0.0
        )

        final_score = (

            # Domain-specific evidence
            0.45
            *
            technical_normalized

            +

            # Exact lexical relevance
            0.25
            *
            keyword_normalized

            +

            # Semantic relevance
            0.15
            *
            cross_normalized

            +

            # Query-term overlap
            0.15
            *
            term_overlap
        )

        return final_score

    # ============================================================
    # MAIN RERANK FUNCTION
    # ============================================================

    def rerank(
        self,
        query,
        candidates,
        top_k=5
    ):
        """
        Re-rank retrieved brochure chunks using:

        1. Technical evidence
        2. Keyword matching
        3. CrossEncoder semantic relevance
        4. Term overlap
        """

        if not candidates:
            return []

        pairs = []

        valid_candidates = []

        # ========================================================
        # PREPARE CANDIDATES
        # ========================================================

        for candidate in candidates:

            if not isinstance(
                candidate,
                dict
            ):
                continue

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
            f"\nRe-ranking "
            f"{len(pairs)} candidates..."
        )

        # ========================================================
        # CROSS ENCODER
        # ========================================================

        cross_scores = self.model.predict(
            pairs
        )

        # ========================================================
        # CALCULATE SCORES
        # ========================================================

        for candidate, cross_score in zip(
            valid_candidates,
            cross_scores
        ):

            text = str(
                candidate.get(
                    "text",
                    ""
                )
            )

            section = str(
                candidate.get(
                    "section",
                    ""
                )
            )

            keyword_score = (
                self._keyword_score(
                    query,
                    text
                )
            )

            technical_score = (
                self._technical_score(
                    query,
                    text,
                    section
                )
            )

            term_overlap = (
                self._term_overlap(
                    query,
                    text
                )
            )

            final_score = (
                self._calculate_final_score(
                    keyword_score=keyword_score,
                    cross_encoder_score=float(
                        cross_score
                    ),
                    technical_score=technical_score,
                    term_overlap=term_overlap
                )
            )

            candidate[
                "rerank_score"
            ] = float(
                final_score
            )

            candidate[
                "keyword_score"
            ] = float(
                keyword_score
            )

            candidate[
                "cross_encoder_score"
            ] = float(
                cross_score
            )

            candidate[
                "technical_score"
            ] = float(
                technical_score
            )

            candidate[
                "term_overlap"
            ] = float(
                term_overlap
            )

            candidate[
                "cross_encoder_normalized"
            ] = float(
                self._normalize_cross_encoder(
                    cross_score
                )
            )

            candidate[
                "technical_normalized"
            ] = float(
                self._normalize_technical_score(
                    technical_score
                )
            )

        # ========================================================
        # SORT
        # ========================================================

        valid_candidates.sort(
            key=lambda item:
                item.get(
                    "rerank_score",
                    0.0
                ),
            reverse=True
        )

        # ========================================================
        # DEBUG OUTPUT
        # ========================================================

        print(
            "\n## FINAL RERANK SCORES"
        )

        for rank, candidate in enumerate(
            valid_candidates,
            start=1
        ):

            print(
                f"\nRank {rank}"
            )

            print(
                f"Page           : "
                f"{candidate.get('page', '')}"
            )

            print(
                f"Section        : "
                f"{candidate.get('section', '')}"
            )

            print(
                f"Keyword Score  : "
                f"{candidate.get('keyword_score', 0):.4f}"
            )

            print(
                f"CrossEncoder   : "
                f"{candidate.get('cross_encoder_score', 0):.4f}"
            )

            print(
                f"Technical      : "
                f"{candidate.get('technical_score', 0):.4f}"
            )

            print(
                f"Term Overlap   : "
                f"{candidate.get('term_overlap', 0):.4f}"
            )

            print(
                f"Final Score    : "
                f"{candidate.get('rerank_score', 0):.4f}"
            )

        # ========================================================
        # RETURN
        # ========================================================

        return valid_candidates[
            :top_k
        ]


# ================================================================
# TEST
# ================================================================

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
            "section": "engine and transmission specifications",
            "page": 14,
            "text": (
                "ENGINE & TRANSMISSION TECHNICAL "
                "SPECIFICATIONS Engine Type Capacity "
                "Max. Power Max. Torque Transmission Type "
                "mStallion Turbo Charged Multipoint Fuel "
                "Injection (TCMPFi) engine 1.2 L "
                "82 kW @ 5000 r/min 200 Nm @ 1500-3500 "
                "r/min PETROL 6 MT / 6 AT "
                "mStallion Turbo Charged Intercooled "
                "Gasoline Direct injection (TGDi) engine "
                "1.2 L 96 kW @ 5000 r/min 230 Nm "
                "@ 1500-3750 r/min "
                "Turbo Diesel with CRDe 1.5 L "
                "85.8 kW @ 3750 r/min "
                "300 Nm @ 1500-2500 r/min"
            )
        },

        {
            "brand": "mahindra",
            "model": "xuv3xo",
            "section": "engine and performance",
            "page": 6,
            "text": (
                "Perfected performance. Engineered "
                "efficiency. Lead ahead with the most "
                "exciting and peppy engine offering "
                "segment leading power of 96 kW @ "
                "5000 r/min and 230 Nm of torque "
                "@ 1500-3750 r/min."
            )
        },

        {
            "brand": "mahindra",
            "model": "xuv3xo",
            "section": "engine",
            "page": 12,
            "text": (
                "The XUV 3XO is equipped with "
                "powerful engine options."
            )
        },

        {
            "brand": "mahindra",
            "model": "xuv3xo",
            "section": "safety",
            "page": 20,
            "text": (
                "The vehicle is equipped with "
                "multiple airbags and safety features."
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
            f"{result.get('technical_score', 0):.4f}"
        )

        print(
            f"Term Overlap   : "
            f"{result.get('term_overlap', 0):.4f}"
        )

        print(
            f"Final Score    : "
            f"{result.get('rerank_score', 0):.4f}"
        )

        print(
            f"Text           : "
            f"{result.get('text', '')}"
        )


# ================================================================
# RUN
# ================================================================

if __name__ == "__main__":
    main()