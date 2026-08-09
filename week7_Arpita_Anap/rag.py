# Week 7 Assessment – Document Question Answering System (RAG)

## Project: Retrieval-Augmented Generation (RAG)

### Objective

#The aim of this project is to build a simple Document Question Answering System using the Retrieval-Augmented Generation (RAG) approach.

#The system reads a PDF document, extracts its text, converts the content into vector embeddings, stores them in a FAISS vector database, and retrieves the most relevant information when a user asks a question. Finally, the retrieved context is provided to the Gemini language model to generate an accurate and context-aware answer.

# Workflow

# Load the PDF document
# Extract text from the document
# Split the text into smaller chunks
# Generate embeddings for each chunk
# Store embeddings in a FAISS vector database
# Accept a user question
# Retrieve the most relevant chunks
# Generate an answer using Gemini

# Tools & Libraries

#Python
# PyPDF
# Sentence Transformers
# FAISS
# Google Gemini API
# NumPy


# IMPORT LIBRARIES


import os

import faiss
import numpy as np

from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


# PROJECT CONFIGURATION


DOCUMENT_FOLDER = "data"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

GEMINI_MODEL = "gemini-flash-latest"

CHUNK_SIZE = 500

CHUNK_OVERLAP = 100

TOP_K = 3



# LOAD API KEY

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

load_dotenv()

print("Current Working Directory:", os.getcwd())

print("ENV File Exists:", os.path.exists(".env"))

api_key = os.getenv("GEMINI_API_KEY")

print("API Key:", api_key)

if api_key is None:

    print("Gemini API Key not found.")
    print("Please create a .env file.")

    exit()


client = genai.Client(api_key=api_key)



# LOAD EMBEDDING MODEL


print("\nLoading Embedding Model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)

print("✓ Embedding Model Loaded")



# FIND PDF FILE


pdf_files = []

if os.path.exists(DOCUMENT_FOLDER):

    for file in os.listdir(DOCUMENT_FOLDER):

        if file.lower().endswith(".pdf"):

            pdf_files.append(file)

else:

    print("Documents folder not found.")

    exit()


if len(pdf_files) == 0:

    print("No PDF file found inside the documents folder.")

    exit()


pdf_path = os.path.join(
    DOCUMENT_FOLDER,
    pdf_files[0]
)

print("\nUsing PDF :")
print(pdf_path)


# LOAD PDF


print("\nLoading PDF...")

reader = PdfReader(pdf_path)

document_text = ""

for page in reader.pages:

    text = page.extract_text()

    if text:

        document_text += text + "\n"

print("✓ PDF Loaded Successfully")


# SPLIT TEXT INTO CHUNKS


print("\nCreating Text Chunks...")

chunks = []

start = 0

while start < len(document_text):

    end = start + CHUNK_SIZE

    chunk = document_text[start:end].strip()

    if chunk:
        chunks.append(chunk)

    start += CHUNK_SIZE - CHUNK_OVERLAP

print(f"✓ {len(chunks)} Chunks Created")



# GENERATE EMBEDDINGS


print("\nGenerating Embeddings...")

embeddings = embedding_model.encode(
    chunks,
    convert_to_numpy=True
)

embeddings = embeddings.astype("float32")

faiss.normalize_L2(embeddings)

print("✓ Embeddings Generated")


# CREATE FAISS VECTOR DATABASE


print("\nCreating Vector Database...")

embedding_dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(embedding_dimension)

index.add(embeddings)

print("✓ Vector Database Ready")



# ASK USER QUESTION


print("\n" + "=" * 60)

user_question = input("Ask Your Question : ").strip()

if user_question == "":

    print("Please enter a valid question.")

    exit()


# GENERATE QUESTION EMBEDDING

query_embedding = embedding_model.encode(
    [user_question],
    convert_to_numpy=True
)

query_embedding = query_embedding.astype("float32")

faiss.normalize_L2(query_embedding)


# RETRIEVE RELEVANT CHUNKS

print("\nSearching relevant information...")

scores, indices = index.search(
    query_embedding,
    TOP_K
)

relevant_chunks = []

for i in indices[0]:

    if i < len(chunks):

        relevant_chunks.append(
            chunks[i]
        )

# PREPARE CONTEXT

context = "\n\n".join(relevant_chunks)


# CREATE PROMPT

prompt = f"""
You are a helpful Document Question Answering Assistant.

Answer ONLY using the information available in the document context.

Rules:

1. Use only the document context.
2. Do not add outside knowledge.
3. If the answer is not available, reply exactly:

"The information is not available in the provided document."

================ DOCUMENT CONTEXT ================

{context}

=================================================

Question:

{user_question}

Answer:
"""

# GENERATE ANSWER USING GEMINI

print("Generating answer...\n")

response = client.models.generate_content(
    model=GEMINI_MODEL,
    contents=prompt
)

answer = response.text.strip()

# DISPLAY FINAL ANSWER

print("\n" + "=" * 60)

print("Answer")

print("=" * 60)

print(answer)

# DISPLAY SOURCE CHUNKS

print("\n" + "=" * 60)

print("Sources Used")

print("=" * 60)

for number, chunk in enumerate(
    relevant_chunks,
    start=1
):

    print(f"\nSource {number}")

    print("-" * 60)

    print(chunk[:200] + "...")

print("\n" + "=" * 60)

print("Document Question Answering System Ready")

print("=" * 60)

print("Ask another question or type 'exit' to quit.\n")



# ASK MORE QUESTIONS


while True:

    print("-" * 60)

    user_question = input("Ask Your Question : ").strip()

    
    # EXIT PROGRAM

    if user_question.lower() == "exit":

        print("\nThank you for using the Document Question Answering System.")
        print("Goodbye!")

        break

    # EMPTY QUESTION

    if user_question == "":

        print("Please enter a valid question.\n")

        continue

    # GENERATE QUESTION EMBEDDING

    query_embedding = embedding_model.encode(
        [user_question],
        convert_to_numpy=True
    )

    query_embedding = query_embedding.astype("float32")

    faiss.normalize_L2(query_embedding)

    # SEARCH VECTOR DATABASE

    print("\nSearching relevant information...")

    scores, indices = index.search(
        query_embedding,
        TOP_K
    )


    # RETRIEVE RELEVANT CHUNKS


    relevant_chunks = []

    for i in indices[0]:

        if i < len(chunks):

            relevant_chunks.append(
                chunks[i]
            )

    # PREPARE CONTEXT

    context = "\n\n".join(
        relevant_chunks
    )

    # CREATE PROMPT


    prompt = f"""
You are a helpful Document Question Answering Assistant.

Answer ONLY using the information available in the document context.

Rules:

1. Use only the document context.

2. Do not use outside knowledge.

3. Do not make up information.

4. If the answer is not available, reply exactly:

"The information is not available in the provided document."

================ DOCUMENT CONTEXT ================

{context}

=================================================

Question:

{user_question}

Answer:
"""

    # GENERATE ANSWER USING GEMINI

    print("Generating answer...\n")

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    answer = response.text.strip()

    # DISPLAY ANSWER

    print("\n" + "=" * 60)

    print("Answer")

    print("=" * 60)

    print(answer)

    # DISPLAY SOURCE CHUNKS

    print("\n" + "=" * 60)

    print("Sources Used")

    print("=" * 60)

    for number, chunk in enumerate(
        relevant_chunks,
        start=1
    ):

        print(f"\nSource {number}")

        print("-" * 60)

        print(chunk[:200] + "...")


    print("\n" + "=" * 60)

    print("Ask another question or type 'exit' to quit.")

    print("=" * 60)


print("\nProgram Finished Successfully.")