from rag.retriever import HybridRetriever
from rag.reranker import Reranker
from rag.context_builder import ContextBuilder
from generation.gemini_generator import GeminiGenerator

import time

from utils.logger import (
    log_query,
    log_error,
    log_performance
)


class RAGPipeline:

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(self):

        print("\n" + "=" * 70)
        print("INITIALIZING DRIVE WISE RAG PIPELINE")
        print("=" * 70)

        # --------------------------------------------------------
        # Retriever
        # --------------------------------------------------------

        print("\n[1] Loading retriever...")

        self.retriever = HybridRetriever()

        # --------------------------------------------------------
        # Reranker
        # --------------------------------------------------------

        print("\n[2] Loading reranker...")

        self.reranker = Reranker()

        # --------------------------------------------------------
        # Context Builder
        # --------------------------------------------------------

        print("\n[3] Loading context builder...")

        self.context_builder = ContextBuilder(
            max_chunks=5,
            max_characters=12000
        )

        print("✓ Context builder ready")

        # --------------------------------------------------------
        # Gemini Generator
        # --------------------------------------------------------

        print("\n[4] Loading Gemini generator...")

        self.generator = GeminiGenerator()

        print("✓ Gemini generator ready")
        print("\n✓ Full RAG pipeline ready")

    # ============================================================
    # QUERY TYPE DETECTION
    # ============================================================

    def _detect_query_type(self, query):

        query_text = str(query).lower()

        query_types = {

            "power": [
                "power",
                "maximum power",
                "max power",
                "bhp",
                "ps",
                "kw"
            ],

            "torque": [
                "torque",
                "maximum torque",
                "max torque",
                "nm"
            ],

            "engine": [
                "engine",
                "engine type",
                "engine capacity",
                "displacement",
                "cc",
                "litre"
            ],

            "mileage": [
                "mileage",
                "fuel efficiency",
                "fuel economy",
                "kmpl",
                "km/l"
            ],

            "transmission": [
                "transmission",
                "gearbox",
                "automatic",
                "manual",
                "6 mt",
                "6 at",
                "autoshift"
            ],

            "dimensions": [
                "length",
                "width",
                "height",
                "wheelbase",
                "dimension",
                "dimensions"
            ],

            "ground_clearance": [
                "ground clearance",
                "clearance"
            ],

            "boot": [
                "boot",
                "boot space",
                "luggage"
            ],

            "fuel_tank": [
                "fuel tank",
                "tank capacity",
                "fuel capacity"
            ],

            "safety": [
                "safety",
                "airbag",
                "airbags",
                "abs",
                "esc",
                "esp",
                "brake"
            ],

            "sunroof": [
                "sunroof",
                "skyroof"
            ],

            "features": [
                "feature",
                "features",
                "equipment",
                "available",
                "offers"
            ]
        }

        detected = []

        for query_type, keywords in query_types.items():

            if any(
                keyword in query_text
                for keyword in keywords
            ):
                detected.append(query_type)

        return detected

    # ============================================================
    # TECHNICAL EVIDENCE SCORE
    # ============================================================

    def _technical_evidence_score(
        self,
        query,
        candidate
    ):
        """
        Calculate technical evidence relevance.

        This score is query-aware. It gives more importance
        to chunks that directly contain evidence related to
        the user's question.
        """

        text = str(
            candidate.get("text", "")
        ).lower()

        section = str(
            candidate.get("section", "")
        ).lower()

        query_text = str(
            query
        ).lower()

        score = 0.0

        query_types = self._detect_query_type(
            query
        )

        # --------------------------------------------------------
        # Query-specific keywords
        # --------------------------------------------------------

        keyword_groups = {

            "power": [
                "power",
                "max power",
                "maximum power",
                "kw",
                "ps",
                "bhp"
            ],

            "torque": [
                "torque",
                "max torque",
                "maximum torque",
                "nm"
            ],

            "engine": [
                "engine",
                "engine type",
                "capacity",
                "displacement",
                "litre",
                "cc"
            ],

            "mileage": [
                "mileage",
                "fuel efficiency",
                "fuel economy",
                "km/l",
                "kmpl"
            ],

            "transmission": [
                "transmission",
                "gearbox",
                "automatic",
                "manual",
                "6 mt",
                "6 at",
                "autoshift"
            ],

            "dimensions": [
                "length",
                "width",
                "height",
                "wheelbase",
                "dimensions"
            ],

            "ground_clearance": [
                "ground clearance",
                "clearance"
            ],

            "boot": [
                "boot",
                "boot space",
                "luggage"
            ],

            "fuel_tank": [
                "fuel tank",
                "tank capacity",
                "fuel capacity"
            ],

            "safety": [
                "airbag",
                "airbags",
                "abs",
                "esc",
                "esp",
                "safety",
                "brake"
            ],

            "sunroof": [
                "sunroof",
                "skyroof"
            ],

            "features": [
                "feature",
                "features",
                "equipment"
            ]
        }

        # --------------------------------------------------------
        # Direct query keyword evidence
        # --------------------------------------------------------

        relevant_keywords = []

        for query_type in query_types:

            relevant_keywords.extend(
                keyword_groups.get(
                    query_type,
                    []
                )
            )

        for keyword in set(relevant_keywords):

            if keyword in text:

                # Direct phrase match gets stronger score
                if keyword in query_text:

                    score += 2.5

                else:

                    score += 1.5

        # --------------------------------------------------------
        # Query-specific section bonus
        # --------------------------------------------------------

        section_bonus_map = {

            "power": [
                "engine",
                "engine and performance",
                "performance",
                "technical specifications",
                "specifications"
            ],

            "torque": [
                "engine",
                "engine and performance",
                "performance",
                "technical specifications",
                "specifications"
            ],

            "engine": [
                "engine",
                "engine and performance",
                "engine specifications",
                "technical specifications",
                "specifications"
            ],

            "mileage": [
                "engine",
                "engine and performance",
                "performance",
                "technical specifications",
                "specifications"
            ],

            "transmission": [
                "engine",
                "engine and performance",
                "technical specifications",
                "specifications"
            ],

            "dimensions": [
                "dimensions",
                "technical specifications",
                "specifications"
            ],

            "ground_clearance": [
                "dimensions",
                "technical specifications",
                "specifications"
            ],

            "boot": [
                "dimensions",
                "interior",
                "interior and comfort",
                "technical specifications"
            ],

            "fuel_tank": [
                "technical specifications",
                "specifications",
                "engine",
                "engine and performance"
            ],

            "safety": [
                "safety"
            ],

            "sunroof": [
                "exterior",
                "interior",
                "features"
            ],

            "features": [
                "features",
                "exterior",
                "interior",
                "interior and comfort",
                "technology",
                "safety"
            ]
        }

        expected_sections = set()

        for query_type in query_types:

            expected_sections.update(
                section_bonus_map.get(
                    query_type,
                    []
                )
            )

        for expected_section in expected_sections:

            if expected_section in section:

                score += 3.0

                break

        # --------------------------------------------------------
        # Technical units
        # --------------------------------------------------------

        technical_units = [
            "kw",
            "ps",
            "bhp",
            "nm",
            "r/min",
            "rpm",
            "mm",
            "km/l",
            "kmpl",
            "litre",
            "liter",
            "cc"
        ]

        if any(
            unit in text
            for unit in technical_units
        ):

            # Only apply this strongly for technical queries
            if query_types:

                score += 1.5

        return score

    # ============================================================
    # QUERY RELEVANCE CHECK
    # ============================================================

    def _is_relevant_evidence(
        self,
        query,
        candidate
    ):
        """
        Prevent obviously unrelated chunks from entering
        the final evidence set.
        """

        query_types = self._detect_query_type(
            query
        )

        if not query_types:

            return True

        text = str(
            candidate.get("text", "")
        ).lower()

        section = str(
            candidate.get("section", "")
        ).lower()

        # --------------------------------------------------------
        # Query-specific evidence terms
        # --------------------------------------------------------

        evidence_terms = {

            "power": [
                "power",
                "kw",
                "ps",
                "bhp"
            ],

            "torque": [
                "torque",
                "nm"
            ],

            "engine": [
                "engine",
                "capacity",
                "cc",
                "litre",
                "liter"
            ],

            "mileage": [
                "mileage",
                "fuel efficiency",
                "kmpl",
                "km/l"
            ],

            "transmission": [
                "transmission",
                "automatic",
                "manual",
                "gearbox"
            ],

            "dimensions": [
                "length",
                "width",
                "height",
                "wheelbase"
            ],

            "ground_clearance": [
                "ground clearance",
                "clearance"
            ],

            "boot": [
                "boot",
                "luggage"
            ],

            "fuel_tank": [
                "fuel tank",
                "tank capacity",
                "fuel capacity"
            ],

            "safety": [
                "airbag",
                "abs",
                "esc",
                "esp",
                "safety",
                "brake"
            ],

            "sunroof": [
                "sunroof",
                "skyroof"
            ],

            "features": [
                "feature",
                "features",
                "equipment"
            ]
        }

        relevant_terms = []

        for query_type in query_types:

            relevant_terms.extend(
                evidence_terms.get(
                    query_type,
                    []
                )
            )

        # --------------------------------------------------------
        # Direct text evidence
        # --------------------------------------------------------

        direct_matches = sum(
            1
            for term in set(relevant_terms)
            if term in text
        )

        if direct_matches > 0:

            return True

        # --------------------------------------------------------
        # Section evidence
        # --------------------------------------------------------

        for query_type in query_types:

            if query_type == "safety":
                if "safety" in section:
                    return True

            elif query_type in [
                "power",
                "torque",
                "engine",
                "mileage",
                "transmission"
            ]:

                if (
                    "engine" in section
                    or
                    "performance" in section
                    or
                    "specification" in section
                ):

                    return True

            elif query_type in [
                "dimensions",
                "ground_clearance",
                "boot"
            ]:

                if "dimension" in section:

                    return True

        return False

    # ============================================================
    # REMOVE DUPLICATE CHUNKS
    # ============================================================

    def _deduplicate_candidates(
        self,
        candidates
    ):

        unique = []

        seen = set()

        for candidate in candidates:

            text = str(
                candidate.get("text", "")
            ).strip().lower()

            page = str(
                candidate.get("page", "")
            )

            section = str(
                candidate.get("section", "")
            ).lower()

            key = (
                text[:500],
                page,
                section
            )

            if key in seen:

                continue

            seen.add(key)

            unique.append(
                candidate
            )

        return unique

    # ============================================================
    # PRIORITIZE TECHNICAL EVIDENCE
    # ============================================================

    def _prioritize_evidence(
        self,
        query,
        candidates,
        top_k=5
    ):

        if not candidates:

            return []

        # --------------------------------------------------------
        # Remove duplicates first
        # --------------------------------------------------------

        candidates = self._deduplicate_candidates(
            candidates
        )

        scored_candidates = []

        for candidate in candidates:

            item = candidate.copy()

            # ----------------------------------------------------
            # Technical score
            # ----------------------------------------------------

            technical_score = (
                self._technical_evidence_score(
                    query=query,
                    candidate=item
                )
            )

            item["technical_score"] = (
                technical_score
            )

            # ----------------------------------------------------
            # Existing reranker score
            # ----------------------------------------------------

            rerank_score = float(
                item.get(
                    "rerank_score",
                    item.get(
                        "final_score",
                        0.0
                    )
                )
            )

            # ----------------------------------------------------
            # Relevance check
            # ----------------------------------------------------

            relevant = self._is_relevant_evidence(
                query=query,
                candidate=item
            )

            item["evidence_relevant"] = relevant

            # ----------------------------------------------------
            # Evidence score
            #
            # Reranker remains important.
            # Technical evidence adds query-specific priority.
            # ----------------------------------------------------

            item["evidence_score"] = (
                rerank_score * 0.80
                +
                technical_score * 0.20
            )

            # Strong penalty for clearly unrelated chunks
            if not relevant:

                item["evidence_score"] -= 1.0

            scored_candidates.append(
                item
            )

        # --------------------------------------------------------
        # Sort
        # --------------------------------------------------------

        scored_candidates.sort(
            key=lambda item: item.get(
                "evidence_score",
                -999
            ),
            reverse=True
        )

        # --------------------------------------------------------
        # Prefer relevant evidence
        # --------------------------------------------------------

        relevant_candidates = [
            item
            for item in scored_candidates
            if item.get(
                "evidence_relevant",
                False
            )
        ]

        # --------------------------------------------------------
        # If enough relevant chunks exist,
        # use only relevant chunks.
        # --------------------------------------------------------

        if len(relevant_candidates) >= top_k:

            return relevant_candidates[:top_k]

        # --------------------------------------------------------
        # Otherwise fill remaining slots.
        # --------------------------------------------------------

        selected = list(
            relevant_candidates
        )

        for item in scored_candidates:

            if item in selected:

                continue

            selected.append(
                item
            )

            if len(selected) >= top_k:

                break

        return selected[:top_k]

    # ============================================================
    # RETRIEVE + RERANK
    # ============================================================

    def retrieve_and_rerank(
        self,
        query,
        brand,
        model,
        retrieval_top_k=30,
        rerank_top_k=5
    ):

        # ========================================================
        # STEP 1 — HYBRID RETRIEVAL
        # ========================================================

        print("\n" + "=" * 70)
        print("STEP 1 — HYBRID RETRIEVAL")
        print("=" * 70)

        retrieval_start = time.perf_counter()

        retrieved = self.retriever.search(
            query=query,
            brand=brand,
            model=model,
            top_k=retrieval_top_k
        )

        retrieval_time = (
            time.perf_counter()
            - retrieval_start
        )

        print(
            f"\nRetrieved chunks: "
            f"{len(retrieved)}"
        )

        print(
            f"Retrieval time: "
            f"{retrieval_time:.4f} sec"
        )

        if not retrieved:

            return (
                [],
                retrieval_time,
                0.0,
                0.0
            )

        # ========================================================
        # STEP 2 — CROSS-ENCODER RERANKING
        # ========================================================

        print("\n" + "=" * 70)
        print("STEP 2 — CROSS-ENCODER RERANKING")
        print("=" * 70)

        reranking_start = time.perf_counter()

        rerank_candidates = self.reranker.rerank(
            query=query,
            candidates=retrieved,
            top_k=min(
                max(
                    rerank_top_k * 3,
                    10
                ),
                len(retrieved)
            )
        )

        reranking_time = (
            time.perf_counter()
            - reranking_start
        )

        print(
            f"\nReranked candidates: "
            f"{len(rerank_candidates)}"
        )

        print(
            f"Reranking time: "
            f"{reranking_time:.4f} sec"
        )

        if not rerank_candidates:

            return (
                [],
                retrieval_time,
                reranking_time,
                0.0
            )

        # ========================================================
        # STEP 3 — TECHNICAL EVIDENCE PRIORITIZATION
        # ========================================================

        print("\n" + "=" * 70)
        print("STEP 3 — TECHNICAL EVIDENCE PRIORITIZATION")
        print("=" * 70)

        evidence_start = time.perf_counter()

        final_candidates = self._prioritize_evidence(
            query=query,
            candidates=rerank_candidates,
            top_k=rerank_top_k
        )

        evidence_time = (
            time.perf_counter()
            - evidence_start
        )

        print(
            f"\nFinal evidence chunks: "
            f"{len(final_candidates)}"
        )

        print(
            f"Evidence ranking time: "
            f"{evidence_time:.4f} sec"
        )

        # ========================================================
        # FINAL EVIDENCE RANKING
        # ========================================================

        print("\n## FINAL EVIDENCE RANKING")

        for rank, candidate in enumerate(
            final_candidates,
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
                f"Rerank Score   : "
                f"{candidate.get('rerank_score', 0):.4f}"
            )

            print(
                f"Technical      : "
                f"{candidate.get('technical_score', 0):.4f}"
            )

            print(
                f"Relevant       : "
                f"{candidate.get('evidence_relevant', False)}"
            )

            print(
                f"Evidence Score : "
                f"{candidate.get('evidence_score', 0):.4f}"
            )

            print(
                f"Text           : "
                f"{candidate.get('text', '')[:500]}"
            )

        return (
            final_candidates,
            retrieval_time,
            reranking_time,
            evidence_time
        )

    # ============================================================
    # COMPLETE RAG QUERY
    # ============================================================

    def answer(
        self,
        query,
        brand,
        model,
        retrieval_top_k=30,
        rerank_top_k=5
    ):

        total_start = time.perf_counter()

        retrieval_time = 0.0
        reranking_time = 0.0
        evidence_time = 0.0
        context_time = 0.0
        generation_time = 0.0

        # ========================================================
        # LOG QUERY
        # ========================================================

        try:

            log_query(
                query=query,
                brand=brand,
                model=model
            )

        except Exception as error:

            print(
                f"⚠ Query logging failed: {error}"
            )

        # ========================================================
        # STEP 1-3 — RETRIEVAL + RERANK + EVIDENCE
        # ========================================================

        try:

            (
                results,
                retrieval_time,
                reranking_time,
                evidence_time
            ) = self.retrieve_and_rerank(
                query=query,
                brand=brand,
                model=model,
                retrieval_top_k=retrieval_top_k,
                rerank_top_k=rerank_top_k
            )

        except Exception as error:

            print(
                f"\n✗ Retrieval pipeline error: {error}"
            )

            try:

                log_error(
                    error=str(error),
                    query=query,
                    brand=brand,
                    model=model
                )

            except Exception:
                pass

            total_time = (
                time.perf_counter()
                - total_start
            )

            return {
                "answer": (
                    "The available brochure information "
                    "does not clearly specify this."
                ),
                "sources": [],
                "retrieved_chunks": 0,
                "context_characters": 0,
                "retrieval_time": retrieval_time,
                "reranking_time": reranking_time,
                "evidence_time": evidence_time,
                "context_time": context_time,
                "generation_time": generation_time,
                "response_time": total_time
            }

        # ========================================================
        # NO RESULTS
        # ========================================================

        if not results:

            total_time = (
                time.perf_counter()
                - total_start
            )

            try:

                log_performance(
                    retrieval_time,
                    reranking_time,
                    context_time,
                    generation_time,
                    total_time
                )

            except Exception as error:

                print(
                    f"⚠ Performance logging failed: {error}"
                )

            return {
                "answer": (
                    "The available brochure information "
                    "does not clearly specify this."
                ),
                "sources": [],
                "retrieved_chunks": 0,
                "context_characters": 0,
                "retrieval_time": retrieval_time,
                "reranking_time": reranking_time,
                "evidence_time": evidence_time,
                "context_time": context_time,
                "generation_time": generation_time,
                "response_time": total_time
            }

        # ========================================================
        # STEP 4 — CONTEXT BUILDING
        # ========================================================

        print("\n" + "=" * 70)
        print("STEP 4 — CONTEXT BUILDING")
        print("=" * 70)

        context_start = time.perf_counter()

        try:

            context = (
                self.context_builder.build_context(
                    results
                )
            )

            sources = (
                self.context_builder.build_sources(
                    results
                )
            )

        except Exception as error:

            print(
                f"\n✗ Context building error: {error}"
            )

            try:

                log_error(
                    error=str(error),
                    query=query,
                    brand=brand,
                    model=model
                )

            except Exception:
                pass

            context = ""
            sources = []

        context_time = (
            time.perf_counter()
            - context_start
        )

        print(
            f"\nContext chunks: "
            f"{len(results)}"
        )

        print(
            f"Context characters: "
            f"{len(context)}"
        )

        print(
            f"Context time: "
            f"{context_time:.4f} sec"
        )

        # ========================================================
        # EMPTY CONTEXT
        # ========================================================

        if not context.strip():

            total_time = (
                time.perf_counter()
                - total_start
            )

            try:

                log_error(
                    error="Empty context generated",
                    query=query,
                    brand=brand,
                    model=model
                )

                log_performance(
                    retrieval_time,
                    reranking_time,
                    context_time,
                    generation_time,
                    total_time
                )

            except Exception as error:

                print(
                    f"⚠ Logging failed: {error}"
                )

            return {
                "answer": (
                    "The available brochure information "
                    "does not clearly specify this."
                ),
                "sources": sources,
                "retrieved_chunks": len(results),
                "context_characters": 0,
                "retrieval_time": retrieval_time,
                "reranking_time": reranking_time,
                "evidence_time": evidence_time,
                "context_time": context_time,
                "generation_time": generation_time,
                "response_time": total_time
            }

        # ========================================================
        # STEP 5 — GEMINI GENERATION
        # ========================================================

        print("\n" + "=" * 70)
        print("STEP 5 — GEMINI ANSWER GENERATION")
        print("=" * 70)

        generation_start = time.perf_counter()

        generated = None

        try:

            generated = (
                self.generator.generate_answer(
                    question=query,
                    brand=brand,
                    model=model,
                    chunks=results
                )
            )

        except Exception as error:

            print(
                f"\n✗ Generation error: {error}"
            )

            try:

                log_error(
                    error=str(error),
                    query=query,
                    brand=brand,
                    model=model
                )

            except Exception:
                pass

            generated = {
                "answer": (
                    "The brochure information was retrieved "
                    "successfully, but the answer generation "
                    "service is currently unavailable."
                ),
                "sources": sources,
                "error": str(error)
            }

        generation_time = (
            time.perf_counter()
            - generation_start
        )

        print(
            f"Generation time: "
            f"{generation_time:.4f} sec"
        )

        # ========================================================
        # GENERATION RESULT
        # ========================================================

        if generated is None:

            generated = {
                "answer": (
                    "The brochure information was retrieved "
                    "successfully, but the answer could not "
                    "be generated."
                ),
                "sources": sources
            }

        final_answer = generated.get(
            "answer",
            ""
        )

        generator_sources = generated.get(
            "sources",
            []
        )

        # ========================================================
        # SOURCE SELECTION
        # ========================================================

        if generator_sources:

            final_sources = generator_sources

        else:

            final_sources = sources

        # ========================================================
        # TOTAL TIME
        # ========================================================

        total_time = (
            time.perf_counter()
            - total_start
        )

        # ========================================================
        # PERFORMANCE LOGGING
        # ========================================================

        try:

            log_performance(
                retrieval_time,
                reranking_time,
                context_time,
                generation_time,
                total_time
            )

        except Exception as error:

            print(
                f"⚠ Performance logging failed: "
                f"{error}"
            )

            try:

                log_error(
                    error=str(error),
                    query=query,
                    brand=brand,
                    model=model
                )

            except Exception:
                pass

        # ========================================================
        # GENERATION ERROR LOGGING
        # ========================================================

        if generated.get("error"):

            try:

                log_error(
                    error=generated.get("error"),
                    query=query,
                    brand=brand,
                    model=model
                )

            except Exception:
                pass

        # ========================================================
        # FINAL RESPONSE
        # ========================================================

        return {
            "answer": final_answer,
            "sources": final_sources,
            "retrieved_chunks": len(results),
            "context_characters": len(context),
            "retrieval_time": retrieval_time,
            "reranking_time": reranking_time,
            "evidence_time": evidence_time,
            "context_time": context_time,
            "generation_time": generation_time,
            "response_time": total_time
        }


# ================================================================
# TEST
# ================================================================

def main():

    print("\n" + "=" * 70)
    print("DRIVE WISE - COMPLETE RAG PIPELINE TEST")
    print("=" * 70)

    # ------------------------------------------------------------
    # Vehicle
    # ------------------------------------------------------------

    brand = "mahindra"
    model = "xuv3xo"

    # ------------------------------------------------------------
    # Question
    # ------------------------------------------------------------

    query = (
        "What is the maximum power "
        "of the XUV 3XO?"
    )

    # ------------------------------------------------------------
    # Initialize pipeline
    # ------------------------------------------------------------

    pipeline = RAGPipeline()

    # ------------------------------------------------------------
    # Run pipeline
    # ------------------------------------------------------------

    result = pipeline.answer(
        query=query,
        brand=brand,
        model=model,
        retrieval_top_k=30,
        rerank_top_k=5
    )

    # ------------------------------------------------------------
    # Final Answer
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL ANSWER")
    print("=" * 70)

    print(
        f"\n{result.get('answer', '')}"
    )

    # ------------------------------------------------------------
    # Sources
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("SOURCES")
    print("=" * 70)

    sources = result.get(
        "sources",
        []
    )

    if not sources:

        print("\nNo sources available.")

    else:

        for index, source in enumerate(
            sources,
            start=1
        ):

            print(
                f"\nSource {index}"
            )

            print(
                f"Brand   : "
                f"{source.get('brand', '')}"
            )

            print(
                f"Model   : "
                f"{source.get('model', '')}"
            )

            print(
                f"Section : "
                f"{source.get('section', '')}"
            )

            print(
                f"Page    : "
                f"{source.get('page', '')}"
            )

            print(
                f"Brochure: "
                f"{source.get('brochure', '')}"
            )

    # ------------------------------------------------------------
    # Pipeline statistics
    # ------------------------------------------------------------

    print("\n" + "=" * 70)
    print("PIPELINE STATISTICS")
    print("=" * 70)

    print(
        f"\nRetrieved chunks : "
        f"{result.get('retrieved_chunks', 0)}"
    )

    print(
        f"Context chars    : "
        f"{result.get('context_characters', 0)}"
    )

    print(
        f"Retrieval time   : "
        f"{result.get('retrieval_time', 0):.4f} sec"
    )

    print(
        f"Reranking time   : "
        f"{result.get('reranking_time', 0):.4f} sec"
    )

    print(
        f"Evidence time    : "
        f"{result.get('evidence_time', 0):.4f} sec"
    )

    print(
        f"Context time     : "
        f"{result.get('context_time', 0):.4f} sec"
    )

    print(
        f"Generation time  : "
        f"{result.get('generation_time', 0):.4f} sec"
    )

    print(
        f"Total time       : "
        f"{result.get('response_time', 0):.4f} sec"
    )

    print(
        "\n✓ COMPLETE RAG PIPELINE TEST FINISHED"
    )


# ================================================================
# RUN
# ================================================================

if __name__ == "__main__":
    main()

