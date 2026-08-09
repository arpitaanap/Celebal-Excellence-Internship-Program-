import re


class QueryAnalyzer:

    # ============================================================
    # STOP WORDS
    # ============================================================

    STOP_WORDS = {
        "the",
        "is",
        "are",
        "a",
        "an",
        "does",
        "do",
        "did",
        "has",
        "have",
        "had",
        "what",
        "which",
        "how",
        "many",
        "much",
        "can",
        "could",
        "would",
        "will",
        "this",
        "that",
        "it",
        "its",
        "of",
        "to",
        "for",
        "and",
        "in",
        "on",
        "with",
        "from",
        "about",
        "available",
        "feature",
        "features",
        "vehicle",
        "car",
    }

    # ============================================================
    # FEATURE QUESTION PATTERNS
    # ============================================================

    FEATURE_PATTERNS = [
        r"\bdoes\b.*\bhave\b",
        r"\bhas\b.*\b",
        r"\bis\b.*\bavailable\b",
        r"\bcomes?\s+with\b",
        r"\bavailable\b",
        r"\boffer(s)?\b",
        r"\bfeature\b",
    ]

    # ============================================================
    # SPECIFICATION PATTERNS
    # ============================================================

    SPECIFICATION_PATTERNS = [
        r"\bhow many\b",
        r"\bhow much\b",
        r"\bwhat is\b",
        r"\bwhat are\b",
        r"\bwhat\s+type\b",
        r"\bcapacity\b",
        r"\bengine\b",
        r"\bpower\b",
        r"\btorque\b",
        r"\bprice\b",
        r"\bseats?\b",
        r"\bdimensions?\b",
        r"\bweight\b",
        r"\bmileage\b",
        r"\bground clearance\b",
    ]

    # ============================================================
    # TOKENIZE
    # ============================================================

    @classmethod
    def tokenize(cls, text):

        words = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower()
        )

        return [
            word
            for word in words
            if word not in cls.STOP_WORDS
        ]

    # ============================================================
    # EXTRACT IMPORTANT TERMS
    # ============================================================

    @classmethod
    def extract_terms(cls, query):

        return cls.tokenize(query)

    # ============================================================
    # DETECT FEATURE QUESTION
    # ============================================================

    @classmethod
    def is_feature_question(cls, query):

        query = query.lower().strip()

        for pattern in cls.FEATURE_PATTERNS:

            if re.search(pattern, query):

                return True

        return False

    # ============================================================
    # DETECT SPECIFICATION QUESTION
    # ============================================================

    @classmethod
    def is_specification_question(cls, query):

        query = query.lower().strip()

        for pattern in cls.SPECIFICATION_PATTERNS:

            if re.search(pattern, query):

                return True

        return False

    # ============================================================
    # ANALYZE QUESTION
    # ============================================================

    @classmethod
    def analyze(cls, query):

        terms = cls.extract_terms(query)

        is_feature = cls.is_feature_question(query)

        is_specification = cls.is_specification_question(query)

        if is_feature:

            intent = "feature_existence"

        elif is_specification:

            intent = "specification"

        else:

            intent = "general"

        return {
            "query": query,
            "terms": terms,
            "intent": intent,
            "is_feature_question": is_feature,
            "is_specification_question": is_specification,
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    questions = [
        "Does the Thar have a sunroof?",
        "How many seats does the Thar have?",
        "What safety features are available?",
        "What engine does the Thar have?",
        "Does the Thar have Apple CarPlay?",
    ]

    for question in questions:

        print("\nQuestion:")
        print(question)

        print("\nAnalysis:")

        result = QueryAnalyzer.analyze(
            question
        )

        print(result)