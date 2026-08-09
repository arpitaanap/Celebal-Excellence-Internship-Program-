import os

from dotenv import load_dotenv
from google import genai


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("API key loaded:", bool(api_key))


if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY not found in .env file."
    )


# ============================================================
# CREATE GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=api_key
)


# ============================================================
# TEST ONE MODEL
# ============================================================

model = "gemini-3.6-flash"

print("\n" + "=" * 60)
print("Testing Gemini model:", model)
print("=" * 60)


try:

    response = client.models.generate_content(
        model=model,
        contents="Reply with exactly: Gemini is working."
    )

    print("\nSUCCESS")
    print("Response:")
    print(response.text)


except Exception as e:

    print("\nFAILED")

    print(
        "Error type:",
        type(e).__name__
    )

    print(
        "Error message:"
    )

    print(e)