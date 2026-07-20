# CELL 1
# ==========================================================
# Install Required Packages
# ==========================================================

!pip -q install sentence-transformers
!pip -q install faiss-cpu
!pip -q install networkx
!pip -q install openai
!pip -q install tqdm
!pip -q install pyarrow

print("✅ All Packages Installed")

# CELL 2
# ==========================================================
# Import Libraries
# ==========================================================

import os
import json
import pickle
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

import networkx as nx
import faiss

from tqdm import tqdm

from sentence_transformers import SentenceTransformer

from openai import OpenAI

warnings.filterwarnings("ignore")

print("✅ Libraries Imported")

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


# CELL 5
# ==========================================================
# Artifact Paths
# ==========================================================

CHUNKS_PATH = CHUNKS_DIR / "chunks.parquet"

EMBEDDINGS_PATH = EMBEDDING_DIR / "embeddings.npy"

FAISS_PATH = VECTOR_DIR / "faiss.index"

GRAPH_PATH = KG_DIR / "knowledge_graph.gpickle"

# CELL 6
# ==========================================================
# Load Project Artifacts
# ==========================================================

import pickle

print("="*70)
print("Loading Project Artifacts")
print("="*70)

# ----------------------------------------------------------
# Load Chunks
# ----------------------------------------------------------

chunks = pd.read_parquet(CHUNKS_PATH)

print(f"✅ Chunks Loaded              : {len(chunks):,}")

# ----------------------------------------------------------
# Load Embeddings
# ----------------------------------------------------------

embeddings = np.load(EMBEDDINGS_PATH)

print(f"✅ Embeddings Loaded          : {embeddings.shape}")

# ----------------------------------------------------------
# Load FAISS Index
# ----------------------------------------------------------

faiss_index = faiss.read_index(str(FAISS_PATH))

print(f"✅ FAISS Index Loaded")

# ----------------------------------------------------------
# Load Knowledge Graph
# ----------------------------------------------------------

with open(GRAPH_PATH, "rb") as f:

    kg = pickle.load(f)

print(f"✅ Knowledge Graph Loaded")

print(f"   Nodes : {kg.number_of_nodes():,}")
print(f"   Edges : {kg.number_of_edges():,}")

print("="*70)
print("Artifacts Loaded Successfully")

# CELL 7
# ==========================================================
# Validate Loaded Artifacts
# ==========================================================

print("="*70)
print("Validating Artifacts")
print("="*70)

assert len(chunks) == embeddings.shape[0], \
    "Mismatch between chunks and embeddings."

assert faiss_index.ntotal == len(chunks), \
    "Mismatch between FAISS index and chunks."

assert kg.number_of_nodes() > 0, \
    "Knowledge Graph is empty."

assert kg.number_of_edges() > 0, \
    "Knowledge Graph contains no edges."

print("✅ Chunks          :", len(chunks))
print("✅ Embeddings      :", embeddings.shape)
print("✅ FAISS Vectors   :", faiss_index.ntotal)
print("✅ Graph Nodes     :", kg.number_of_nodes())
print("✅ Graph Edges     :", kg.number_of_edges())

print("\nAll validations passed.")

# CELL 8
# ==========================================================
# Load Sentence Transformer
# ==========================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

print("Loading embedding model...")

embedding_model = SentenceTransformer(MODEL_NAME)

print("✅ Model Loaded")
print(MODEL_NAME)

# CELL 9
# ==========================================================
# Generate Query Embedding
# ==========================================================

def embed_query(question: str):

    """
    Generate embedding for user query.
    """

    embedding = embedding_model.encode(
        question,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embedding.astype("float32")

# CELL 10
# ==========================================================
# FAISS Semantic Retrieval
# ==========================================================

def retrieve_chunks(
    question: str,
    top_k: int = 5
):

    """
    Retrieve top-k most similar chunks.
    """

    query_embedding = embed_query(question)

    distances, indices = faiss_index.search(

        np.array([query_embedding]),

        top_k

    )

    results = []

    for rank, idx in enumerate(indices[0]):

        row = chunks.iloc[idx]

        results.append({

            "rank": rank + 1,

            "score": float(distances[0][rank]),

            "chunk_id": row["Chunk_ID"],

            "document_id": row["Document_ID"],

            "file_name": row["File_Name"],

            "chunk_text": row["Chunk_Text"]

        })

    return results

# CELL 11
# ==========================================================
# Test Semantic Search
# ==========================================================

question = "What PPE should be worn while operating machinery?"

results = retrieve_chunks(question, top_k=5)

print("="*80)
print("Question")
print("="*80)
print(question)

print("\n")

print("="*80)
print("Retrieved Chunks")
print("="*80)

for chunk in results:

    print(f"\nRank : {chunk['rank']}")

    print(f"Score : {chunk['score']:.4f}")

    print(f"Chunk : {chunk['chunk_id']}")

    print(f"File  : {chunk['file_name']}")

    print("-"*70)

    print(chunk["chunk_text"])

    print()

# CELL 12
# ==========================================================
# Industrial Entity Extraction
# ==========================================================

import re

SAFETY = {
    "danger","warning","caution","notice","ppe","helmet",
    "gloves","goggles","ear protection","eye protection",
    "respirator","flammable","hot","hazard","electric",
    "voltage","high voltage","lockout","tagout",
    "emergency","fire","explosion","toxic","chemical"
}

MAINTENANCE = {
    "inspect","replace","clean","lubricate","tighten",
    "repair","maintenance","service","adjust","remove",
    "install","check","calibrate","grease","oil"
}

EQUIPMENT = {
    "pump","motor","compressor","gearbox","bearing",
    "valve","filter","sensor","switch","fan",
    "conveyor","cylinder","belt","pipe","tank",
    "engine","machine","generator","transformer",
    "battery","hydraulic","pneumatic"
}

def extract_entities(text):

    text = str(text).lower()

    entities = []

    for keyword in SAFETY:
        if keyword in text:
            entities.append(keyword.title())

    for keyword in MAINTENANCE:
        if keyword in text:
            entities.append(keyword.title())

    for keyword in EQUIPMENT:
        if keyword in text:
            entities.append(keyword.title())

    for code in re.findall(r"[A-Z]{2,5}-?\d{2,6}", text.upper()):
        entities.append(code)

    return sorted(list(set(entities)))

# CELL 13
# ==========================================================
# Expand Knowledge Graph (Fixed)
# ==========================================================

def expand_graph(entities, max_neighbors=5):

    related_entities = set()

    for entity in entities:

        if not kg.has_node(entity):
            continue

        count = 0

        for neighbor in kg.neighbors(entity):

            edge = kg.get_edge_data(entity, neighbor)

            if edge["relation"] != "co_occurs":
                continue

            related_entities.add(neighbor)

            count += 1

            if count >= max_neighbors:
                break

    return list(related_entities)

# CELL 14
# ==========================================================
# Retrieve Graph Chunks
# ==========================================================

def retrieve_graph_chunks(related_entities, max_chunks=30):

    graph_chunks = []
    visited = set()

    for entity in related_entities:

        if not kg.has_node(entity):
            continue

        for neighbor in kg.neighbors(entity):

            edge = kg.get_edge_data(entity, neighbor)

            if edge["relation"] != "mentions":
                continue

            if neighbor in visited:
                continue

            visited.add(neighbor)

            row = chunks[chunks["Chunk_ID"] == neighbor]

            if len(row) == 0:
                continue

            row = row.iloc[0]

            graph_chunks.append({

                "chunk_id": row["Chunk_ID"],
                "document_id": row["Document_ID"],
                "file_name": row["File_Name"],
                "chunk_text": row["Chunk_Text"]

            })

            # HARD LIMIT
            if len(graph_chunks) >= max_chunks:
                return graph_chunks

    return graph_chunks

# CELL 15
# ==========================================================
# Merge Retrieved Context
# ==========================================================

def merge_context(semantic_chunks, graph_chunks):

    merged = {}

    for chunk in semantic_chunks:

        merged[chunk["chunk_id"]] = chunk

    for chunk in graph_chunks:

        if chunk["chunk_id"] not in merged:

            merged[chunk["chunk_id"]] = chunk

    return list(merged.values())

# CELL 16
import re

# ==========================================================
# Hybrid Graph-RAG Retrieval
# ==========================================================

def hybrid_retrieval(question, top_k=5, graph_top_k=20):

    # ----------------------------
    # Step 1
    # Semantic Search
    # ----------------------------

    semantic_chunks = retrieve_chunks(question, top_k)

    # ----------------------------
    # Step 2
    # Extract entities from QUESTION
    # ----------------------------

    entities = extract_entities(question)

    # Fallback if nothing extracted from question
    if len(entities) == 0:
        text = " ".join(
            c["chunk_text"]
            for c in semantic_chunks
        )
        entities = extract_entities(text)

    # ----------------------------
    # Step 3
    # Graph Expansion
    # ----------------------------

    related_entities = expand_graph(entities)

    # ----------------------------
    # Step 4
    # Retrieve Graph Chunks
    # ----------------------------

    graph_chunks = retrieve_graph_chunks(

        related_entities,

        max_chunks=graph_top_k

    )

    # ----------------------------
    # Step 5
    # Merge
    # ----------------------------

    final_chunks = merge_context(

        semantic_chunks,

        graph_chunks

    )

    return {

        "question": question,

        "semantic_chunks": semantic_chunks,

        "entities": entities,

        "related_entities": related_entities,

        "graph_chunks": graph_chunks,

        "final_chunks": final_chunks

    }

# CELL 17
#test9
result = hybrid_retrieval(
    "What PPE should be worn while operating hydraulic equipment?"
)

print("Entities:", len(result["entities"]))
print("Related:", len(result["related_entities"]))
print("Graph Chunks:", len(result["graph_chunks"]))
print("Final Chunks:", len(result["final_chunks"]))

# CELL 18
# ==========================================================
# Test Hybrid Graph-RAG
# ==========================================================

question = "How should I inspect a hydraulic pump safely?"

result = hybrid_retrieval(question)

print("="*80)
print("Question")
print("="*80)

print(result["question"])

print("\nDetected Entities")

print(result["entities"])

print("\nRelated Graph Entities")

print(result["related_entities"])

print("\nSemantic Chunks")

print(len(result["semantic_chunks"]))

print("Graph Chunks")

print(len(result["graph_chunks"]))

print("Final Chunks")

print(len(result["final_chunks"]))

# CELL 19
# ==========================================================
# Industrial AI Assistant System Prompt
# ==========================================================

SYSTEM_PROMPT = """
You are an Industrial AI Copilot designed to assist engineers,
maintenance technicians, safety officers, and plant operators.

You MUST answer ONLY using the supplied context.

Guidelines:

1. Do not invent information.

2. If the answer is not present in the provided context,
reply:

"I could not find sufficient information in the available documents."

3. Prefer concise technical explanations.

4. Mention safety warnings whenever applicable.

5. If multiple documents provide relevant information,
combine them into a single coherent answer.

6. Never mention that you are an AI language model.

7. Format answers using bullet points whenever appropriate.
"""

# CELL 20
# ==========================================================
# Build Context
# ==========================================================

def build_context(chunks):

    context = []

    for i, chunk in enumerate(chunks, start=1):

        context.append(

            f"""
Source {i}

Document : {chunk['document_id']}

File : {chunk['file_name']}

Content:

{chunk['chunk_text']}
"""
        )

    return "\n\n".join(context)

# CELL 21
# ==========================================================
# Prompt Builder
# ==========================================================

def build_prompt(question, retrieved_chunks):

    context = build_context(retrieved_chunks)

    prompt = f"""
Question

{question}

----------------------------------------

Available Context

{context}

----------------------------------------

Instructions

Answer ONLY from the context above.

If information is missing, clearly state it.

Provide a technical, concise, well-structured answer.
"""

    return prompt

# CELL 22
question = "How should a hydraulic pump be inspected safely?"

retrieval = hybrid_retrieval(question)

prompt = build_prompt(

    question,

    retrieval["final_chunks"]

)

print(prompt[:5000])

# CELL 23
# ==========================================================
# OpenRouter Configuration
# ==========================================================

from google.colab import userdata

# ----------------------------------------------------------
# OpenRouter API Key
# ----------------------------------------------------------

OPENROUTER_API_KEY = userdata.get('OPENROUTER_API_KEY')

# OR directly assign for testing (not recommended for GitHub)
# OPENROUTER_API_KEY = "your_api_key"

if OPENROUTER_API_KEY is None:
    raise ValueError(
        "OPENROUTER_API_KEY environment variable not found. Please set it in Colab secrets."
    )

print("✅ OpenRouter API Key Loaded")

# CELL 24
# ==========================================================
# Initialize OpenRouter Client
# ==========================================================

from openai import OpenAI

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

MODEL_NAME = "deepseek/deepseek-chat-v3-0324"

print("="*60)
print("Model")
print("="*60)

print(MODEL_NAME)

# CELL 25
# ==========================================================
# LLM Answer Generation
# ==========================================================

def generate_answer(prompt):

    """
    Generate answer using DeepSeek Chat V3.
    """

    try:

        response = client.chat.completions.create(

            model=MODEL_NAME,

            messages=[

                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            temperature=0.2,

            max_tokens=1200

        )

        answer = response.choices[0].message.content

        return answer

    except Exception as e:

        return f"LLM Error: {str(e)}"

# CELL 26
# ==========================================================
# Test DeepSeek
# ==========================================================

test_prompt = """
Question:

What is preventive maintenance?

Context:

Preventive maintenance is a scheduled maintenance
strategy performed before equipment failure to
reduce downtime.
"""

answer = generate_answer(test_prompt)

print("="*80)
print(answer)

# CELL 27
# ==========================================================
# Complete Graph-RAG Pipeline
# ==========================================================

import time

def graph_rag_pipeline(question, top_k=5):

    start_time = time.time()

    # ------------------------------------------------------
    # Hybrid Retrieval
    # ------------------------------------------------------

    retrieval = hybrid_retrieval(
        question,
        top_k=top_k
    )

    # ------------------------------------------------------
    # Prompt
    # ------------------------------------------------------

    prompt = build_prompt(
        question,
        retrieval["final_chunks"]
    )

    # ------------------------------------------------------
    # LLM
    # ------------------------------------------------------

    answer = generate_answer(prompt)

    # ------------------------------------------------------
    # Execution Time
    # ------------------------------------------------------

    elapsed = round(
        time.time() - start_time,
        2
    )

    return {

        "question": question,

        "answer": answer,

        "entities": retrieval["entities"],

        "related_entities": retrieval["related_entities"],

        "semantic_chunks": len(
            retrieval["semantic_chunks"]
        ),

        "graph_chunks": len(
            retrieval["graph_chunks"]
        ),

        "total_chunks": len(
            retrieval["final_chunks"]
        ),

        "sources": [

            {

                "chunk_id": c["chunk_id"],
                "document_id": c["document_id"],
        "file_name": c["file_name"],
        "page_number": c.get("page_number"),
        "chunk_number": c.get("chunk_number"),
        "source": c.get("source")

            }

            for c in retrieval["final_chunks"]

        ],

        "response_time": elapsed

    }

# CELL 28
# ==========================================================
# Test Graph-RAG Pipeline
# ==========================================================

question = "What PPE should be worn while operating hydraulic equipment?"

result = graph_rag_pipeline(question)

print("="*80)
print("QUESTION")
print("="*80)

print(result["question"])

print("\n")

print("="*80)
print("ANSWER")
print("="*80)

print(result["answer"])

print("\n")

print("="*80)
print("STATISTICS")
print("="*80)

print("Semantic Chunks :", result["semantic_chunks"])

print("Graph Chunks    :", result["graph_chunks"])

print("Total Chunks    :", result["total_chunks"])

print("Response Time   :", result["response_time"], "seconds")

# CELL 29
# ==========================================================
# Sources Used
# ==========================================================

print("="*80)
print("Retrieved Sources")
print("="*80)

for i, source in enumerate(result["sources"], start=1):

    print(f"\n{i}")

    print("Document :", source["document_id"])

    print("Chunk    :", source["chunk_id"])

    print("File     :", source["file_name"])

