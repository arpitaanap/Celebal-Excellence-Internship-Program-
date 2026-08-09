from retrieval.hybrid_retriever import HybridRetriever


retriever = HybridRetriever()


query = "What is the maximum power of the XUV 3XO?"

results = retriever.search(
    query=query,
    brand="mahindra",
    model="xuv3xo",
    top_k=30
)


print("\n" + "=" * 70)
print("RETRIEVED CANDIDATES")
print("=" * 70)


for number, chunk in enumerate(results, start=1):

    print("\n" + "-" * 70)

    print(f"Result : {number}")
    print(f"Page   : {chunk.get('page')}")
    print(f"Section: {chunk.get('section')}")
    print(f"Keyword Score: {chunk.get('keyword_score')}")
    
    text = str(
        chunk.get("text", "")
    )

    print(f"Text   : {text[:500]}")


print("\n" + "=" * 70)
print("TOTAL:", len(results))
print("=" * 70)