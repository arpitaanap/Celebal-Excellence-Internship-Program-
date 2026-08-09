from gemini_generator import GeminiGenerator


def main():

    generator = GeminiGenerator()


    chunks = [
        {
            "text": (
                "The Thar has front-facing rear seats "
                "with 50:50 split."
            ),
            "section": "interior and comfort",
            "page": 10,
            "brochure": "thar_brochure.pdf"
        }
    ]


    result = generator.generate_answer(
        question="How are the rear seats configured?",
        brand="mahindra",
        model="thar",
        chunks=chunks
    )


    print("\nAnswer:")
    print(result["answer"])


    print("\nSources:")

    for source in result["sources"]:
        print(source)


if __name__ == "__main__":
    main()