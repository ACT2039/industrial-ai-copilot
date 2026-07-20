# CELL 0
# ==========================================================
# Install Required Libraries
# ==========================================================

!pip -q install faiss-cpu
!pip -q install sentence-transformers
!pip -q install openai
!pip -q install pandas
!pip -q install numpy
!pip -q install tqdm

# CELL 1
# ==========================================================
# Imports
# ==========================================================

import os
import json
import faiss
import logging
import numpy as np
import pandas as pd

from pathlib import Path
from datetime import datetime

from sentence_transformers import SentenceTransformer

from openai import OpenAI

from google.colab import userdata

# CELL 2
# ==========================================================
# Configure Logging
# ==========================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger("IndustrialAI")

logger.info("Notebook 7 Started")

# CELL 3
# ==========================================================
# Universal Notebook Setup
# Compatible with VS Code • GitHub • Local Development
# ==========================================================

import sys
from pathlib import Path

# ----------------------------------------------------------
# Step 1: Automatically locate PROJECT_ROOT
# ----------------------------------------------------------
_current_dir = Path.cwd().resolve()
PROJECT_ROOT = None

# Search upwards (max 5 levels) for src/core/config.py
for _ in range(5):
    if (_current_dir / "src" / "core" / "config.py").is_file():
        PROJECT_ROOT = _current_dir
        break
    _current_dir = _current_dir.parent

if PROJECT_ROOT is None:
    raise FileNotFoundError(
        "❌ Could not automatically determine PROJECT_ROOT.\n"
        "Please make sure the notebook is opened from inside the project."
    )

# ----------------------------------------------------------
# Step 2: Add PROJECT_ROOT to Python path (if needed)
# ----------------------------------------------------------
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ----------------------------------------------------------
# Step 3: Import centralized configuration
# ----------------------------------------------------------
from src.core.config import (
    PROJECT_ROOT as CONFIG_ROOT,
    DATA_DIR,
    RAW_DIR,
    PROCESSED_DIR,
    CHUNK_DIR,
    EMBEDDING_DIR,
    VECTOR_DB_DIR,
    KG_DIR,
    INVENTORY_DIR,
    LOG_DIR,
)

# ----------------------------------------------------------
# Step 4: Verify PROJECT_ROOT consistency
# ----------------------------------------------------------
if CONFIG_ROOT != PROJECT_ROOT:
    print("⚠ WARNING: Notebook PROJECT_ROOT differs from config.py PROJECT_ROOT")
    print(f"Notebook : {PROJECT_ROOT}")
    print(f"Config   : {CONFIG_ROOT}")

# Use the centralized PROJECT_ROOT from config.py
PROJECT_ROOT = CONFIG_ROOT

# ----------------------------------------------------------
# Step 5: Verify required directories exist
# ----------------------------------------------------------
required_dirs = [
    DATA_DIR,
    RAW_DIR,
    PROCESSED_DIR,
    CHUNK_DIR,
    EMBEDDING_DIR,
    VECTOR_DB_DIR,
    KG_DIR,
    INVENTORY_DIR,
    LOG_DIR,
]

missing_dirs = [d for d in required_dirs if not d.exists()]

if missing_dirs:
    print("\n❌ Missing Directories:")
    for d in missing_dirs:
        print(f"   - {d}")
    raise FileNotFoundError("One or more required directories are missing.")

# ----------------------------------------------------------
# Step 6: Environment Verification
# ----------------------------------------------------------
print("=" * 65)
print("PROJECT SETUP VERIFICATION SUMMARY")
print("=" * 65)
print(f"PROJECT_ROOT      : {PROJECT_ROOT}")
print(f"DATA_DIR          : {DATA_DIR}")
print(f"RAW_DIR           : {RAW_DIR}")
print(f"PROCESSED_DIR     : {PROCESSED_DIR}")
print(f"CHUNK_DIR         : {CHUNK_DIR}")
print(f"EMBEDDING_DIR     : {EMBEDDING_DIR}")
print(f"VECTOR_DB_DIR     : {VECTOR_DB_DIR}")
print(f"KG_DIR            : {KG_DIR}")
print(f"INVENTORY_DIR     : {INVENTORY_DIR}")
print(f"LOG_DIR           : {LOG_DIR}")
print("-" * 65)
print("✅ Status          : SUCCESS")
print("=" * 65)


# CELL 4
print("="*60)

print("FAISS Index :", (VECTOR_DB_DIR / "faiss.index").exists())

print("FAISS Metadata :", (VECTOR_DB_DIR / "faiss_metadata.parquet").exists())

print("Processed Documents :", (PROCESSED_DIR / "processed_documents.parquet").exists())

print("Text Documents :", (PROCESSED_DIR / "text_documents.parquet").exists())

print("Metadata :", (METADATA_DIR / "metadata.csv").exists())

print("="*60)

# CELL 5
# ==========================================================
# Additional Imports
# ==========================================================

import faiss
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer

# CELL 6
# ==========================================================
# Load FAISS Index
# ==========================================================

FAISS_INDEX_PATH = VECTOR_DB_DIR / "faiss.index"

index = faiss.read_index(str(FAISS_INDEX_PATH))

print("="*60)
print("FAISS Index Loaded Successfully")
print("Total vectors :", index.ntotal)
print("Vector dimension :", index.d)
print("="*60)

# CELL 7
# ==========================================================
# Load FAISS Metadata
# ==========================================================

FAISS_METADATA_PATH = VECTOR_DB_DIR / "faiss_metadata.parquet"

faiss_metadata = pd.read_parquet(FAISS_METADATA_PATH)

print("="*60)
print("Metadata Loaded")
print("Total Records :", len(faiss_metadata))
print("="*60)

display(faiss_metadata.head())

# CELL 8
# ==========================================================
# Inspect Metadata
# ==========================================================

print("Columns:\n")

for col in faiss_metadata.columns:
    print("-", col)

# CELL 9
# ==========================================================
# Load Embedding Model
# ==========================================================

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(EMBEDDING_MODEL)

print("="*60)
print("Embedding Model Loaded")
print(EMBEDDING_MODEL)
print("="*60)

# CELL 10
# ==========================================================
# Query Embedding Function
# ==========================================================

def embed_query(question: str):

    embedding = embedding_model.encode(
        question,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embedding.astype(np.float32)

# CELL 11
# ==========================================================
# Semantic Search
# ==========================================================

def semantic_search(question, top_k=5):

    query_vector = embed_query(question)

    distances, indices = index.search(
        query_vector.reshape(1, -1),
        top_k
    )

    results = faiss_metadata.iloc[indices[0]].copy()

    results["similarity"] = distances[0]

    return results

# CELL 12
# ==========================================================
# Test Retrieval
# ==========================================================

question = "How should pump maintenance be performed?"

results = semantic_search(question)

display(results)

# CELL 13
# ==========================================================
# Display Retrieved Chunks
# ==========================================================

def show_results(results):

    print("="*80)

    for i, row in results.iterrows():

        print(f"\nResult {i+1}")

        print("-"*80)

        print("Similarity :", round(row["similarity"],4))

        print()

        for col in results.columns:

            if col != "similarity":

                print(f"{col}:")

                print(row[col])

                print()

        print("="*80)

# CELL 14
show_results(results)

# CELL 15
# ==========================================================
# Build Chunk Lookup Table
# ==========================================================

chunk_lookup = chunks_df.set_index("Chunk_ID")

print("="*60)
print("Chunk Lookup Created")
print("Total Chunks:", len(chunk_lookup))
print("="*60)

# CELL 16
# ==========================================================
# Enterprise Semantic Search
# ==========================================================

def semantic_search(question, top_k=5):

    query_vector = embed_query(question)

    distances, indices = index.search(
        query_vector.reshape(1, -1),
        top_k
    )

    retrieved_chunks = []

    for distance, idx in zip(distances[0], indices[0]):

        meta = faiss_metadata.iloc[idx]

        chunk = chunk_lookup.loc[meta["Chunk_ID"]]

        retrieved_chunks.append({

            "Similarity": float(distance),

            "Chunk_ID": meta["Chunk_ID"],

            "Document_ID": meta["Document_ID"],

            "File_Name": meta["File_Name"],

            "Page_Number": meta["Page_Number"],

            "Chunk_Number": meta["Chunk_Number"],

            "Chunk_Text": chunk["Chunk_Text"]

        })

    return pd.DataFrame(retrieved_chunks)

# CELL 17
question = "How should HVAC preventive maintenance be performed?"

results = semantic_search(question)

display(results)

# CELL 18
def show_results(results):

    for i, row in results.iterrows():

        print("="*100)

        print(f"Result {i+1}")

        print()

        print("Similarity :", round(row["Similarity"],4))

        print("Document   :", row["File_Name"])

        print("Page       :", row["Page_Number"])

        print("Chunk      :", row["Chunk_Number"])

        print()

        print(row["Chunk_Text"])

        print()

# CELL 19
show_results(results)

# CELL 20
# ==========================================================
# Build RAG Context
# ==========================================================

def build_context(results):

    context = []

    for _, row in results.iterrows():

        context.append(
            f"""
Document : {row['File_Name']}
Page : {row['Page_Number']}
Chunk : {row['Chunk_Number']}

Content:
{row['Chunk_Text']}
"""
        )

    return "\n\n".join(context)

# CELL 21
context = build_context(results)

print(context[:3000])

# CELL 22
# ==========================================================
# Industrial AI Copilot Prompt
# ==========================================================

SYSTEM_PROMPT = """
You are an Industrial AI Maintenance Copilot.

Your job is to answer ONLY using the supplied industrial documents.

Rules:

1. Never invent information.
2. If the answer is not present in the documents, clearly state:
   "The uploaded documentation does not contain enough information."

3. Be concise and technically accurate.

4. Mention equipment names whenever available.

5. Mention safety precautions if applicable.

6. Cite document names whenever possible.

7. Structure the answer professionally.
"""

# CELL 23
# ==========================================================
# Prompt Builder
# ==========================================================

def build_prompt(question, context):

    prompt = f"""
Context
=======

{context}

==================================================

Question

{question}

==================================================

Answer:
"""

    return prompt

# CELL 24
prompt = build_prompt(

    "How do I perform preventive maintenance on an HVAC unit?",

    context

)

print(prompt[:5000])

# CELL 25
from openai import OpenAI
from google.colab import userdata

# CELL 26
client = OpenAI(

    api_key=userdata.get("OPENROUTER_API_KEY"),

    base_url="https://openrouter.ai/api/v1"
)

# CELL 27
MODEL_NAME = "deepseek/deepseek-chat-v3-0324"

# CELL 28
# ==========================================================
# OpenRouter Response
# ==========================================================

def ask_llm(question, context):

    prompt = build_prompt(question, context)

    response = client.chat.completions.create(

        model=MODEL_NAME,

        temperature=0.2,

        max_tokens=800,

        messages=[

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": prompt
            }

        ]

    )

    return response.choices[0].message.content

# CELL 29
answer = ask_llm(

    "How should preventive maintenance of HVAC equipment be performed?",

    context

)

print(answer)

# CELL 30
# ==========================================================
# Industrial AI Copilot
# ==========================================================

def ask_copilot(question, top_k=5):

    retrieved = semantic_search(question, top_k)

    context = build_context(retrieved)

    answer = ask_llm(question, context)

    return {

        "question": question,

        "answer": answer,

        "sources": retrieved,

        "context": context

    }

# CELL 31
response = ask_copilot(

    "What are the lubrication intervals for industrial pumps?"

)

print(response["answer"])

display(response["sources"])

# CELL 32
import json
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = PROJECT_ROOT / "data" / "rag"

OUTPUT_DIR.mkdir(exist_ok=True)

def save_response(result):

    filename = OUTPUT_DIR / f"rag_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    serializable = {
        "question": result["question"],
        "answer": result["answer"],
        "context": result["context"],
        "sources": result["sources"].to_dict(orient="records")
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=4, ensure_ascii=False)

    print(f"Saved to: {filename}")

# CELL 33
result = ask_copilot(
    "What safety precautions should be followed before servicing industrial HVAC equipment?"
)

save_response(result)

print(result["answer"])

