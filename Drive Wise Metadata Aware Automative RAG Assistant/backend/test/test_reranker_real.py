from retrieval.hybrid_retriever import HybridRetriever
from rag.reranker import Reranker


query = "What is the maximum power of the XUV 3XO?"


# ---------------------------------------------------------
# RETRIEVER
# ---------------------------------------------------------

retriever = HybridRetriever()

candidates = retriever.search(
    query=query,
    brand="mahindra",
    model="xuv3xo",
    top_k=30
)


# ---------------------------------------------------------
# FIND IMPORTANT PAGES
# ---------------------------------------------------------

important = []

for candidate in candidates:

    page = candidate.get("page")

    if page in [6, 14]:

        important.append(candidate)


print("\n" + "=" * 70)
print("IMPORTANT RETRIEVED CHUNKS")
print("=" * 70)


for candidate in important:

    print("\n" + "-" * 70)

    print("Page   :", candidate.get("page"))
    print("Section:", candidate.get("section"))
    print("Keyword:", candidate.get("keyword_score"))

    print(
        "Text   :",
        candidate.get("text", "")[:1000]
    )


# ---------------------------------------------------------
# RERANK
# ---------------------------------------------------------

reranker = Reranker()


results = reranker.rerank(
    query=query,
    candidates=important,
    top_k=10
)


print("\n" + "=" * 70)
print("RERANKER SCORES")
print("=" * 70)


for result in results:

    print("\n" + "-" * 70)

    print("Page   :", result.get("page"))
    print("Section:", result.get("section"))

    print(
        "Rerank :",
        result.get("rerank_score")
    )

    print(
        "Text   :",
        result.get("text", "")[:500]
    )