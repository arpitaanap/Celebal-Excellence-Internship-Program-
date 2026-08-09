from generation.gemini_generator import GeminiGenerator


generator = GeminiGenerator()

chunks = [
    {
        "text": "The XUV 3XO is equipped with a 1197 cc turbo petrol engine.",
        "section": "Engine",
        "page": 12,
        "brochure": "X3XO_brochure.pdf"
    },
    {
        "text": "Maximum power is 130 PS and maximum torque is 230 Nm.",
        "section": "Engine Specifications",
        "page": 13,
        "brochure": "X3XO_brochure.pdf"
    }
]


result = generator.generate(
    question="What is the maximum power of the vehicle?",
    brand="Mahindra",
    model="XUV 3XO",
    chunks=chunks
)


print("\n================ ANSWER ================\n")
print(result["answer"])

print("\n================ SOURCES ================\n")
for source in result["sources"]:
    print(source)