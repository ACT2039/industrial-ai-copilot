# CELL 1
# ==========================================================
# Install Libraries
# ==========================================================

!pip -q install faiss-cpu sentence-transformers

# CELL 2
# ==========================================================
# Imports
# ==========================================================

from pathlib import Path

import faiss
import json
import logging
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer

print("Libraries Imported Successfully")

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
        "❌ Could not automatically determine PROJECT_ROOT.\n
"
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
    print("\n
❌ Missing Directories:")
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
# Configure Logger
# ==========================================================

logging.basicConfig(

    filename=LOG_DIR/"notebook06_faiss.log",

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

    force=True

)

logging.info("Notebook 06 Started")

print("Logger Ready")

# CELL 5
# ==========================================================
# Load Embeddings
# ==========================================================

embedding_file = EMBEDDING_DIR / "embeddings.npy"

embeddings = np.load(embedding_file)

print("="*60)
print("Embeddings Loaded")
print("="*60)

print("Shape :", embeddings.shape)

# CELL 6
# ==========================================================
# Load Metadata
# ==========================================================

metadata_file = EMBEDDING_DIR / "embedding_metadata.parquet"

metadata = pd.read_parquet(metadata_file)

print()

print("Metadata Loaded")

print("Records :", len(metadata))

# CELL 7
display(metadata.head())

# CELL 8
# ==========================================================
# Validation
# ==========================================================

assert len(metadata) == embeddings.shape[0]

print("Validation Passed")

# CELL 9
print("="*70)

print("MILESTONE 1 COMPLETED")

print("="*70)

# CELL 10
# ==========================================================
# FAISS Configuration
# ==========================================================

INDEX_TYPE = "IndexFlatIP"

EMBEDDING_DIMENSION = embeddings.shape[1]

print("="*60)
print("FAISS Configuration")
print("="*60)

print("Index Type :", INDEX_TYPE)
print("Embedding Dimension :", EMBEDDING_DIMENSION)
print("Total Embeddings :", embeddings.shape[0])

# CELL 11
# ==========================================================
# FAISS Index Path
# ==========================================================

index_path = VECTOR_DB_DIR / "faiss.index"

print(index_path)

# CELL 12
# ==========================================================
# Load Existing Index (if available)
# ==========================================================

if index_path.exists():

    print("Loading Existing FAISS Index...")

    index = faiss.read_index(str(index_path))

    print("Existing Index Loaded")

else:

    print("Creating New FAISS Index...")

    index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)

# CELL 13
# ==========================================================
# Build FAISS Index
# ==========================================================

if index.ntotal == 0:

    print("Adding embeddings to FAISS...")

    index.add(
        embeddings.astype(np.float32)
    )

    print("Embeddings Added Successfully")

else:

    print("Index already contains vectors.")

# CELL 14
# ==========================================================
# Index Summary
# ==========================================================

print("="*60)

print("FAISS INDEX SUMMARY")

print("="*60)

print("Total Indexed Vectors :", index.ntotal)

print("Embedding Dimension   :", index.d)

# CELL 15
# ==========================================================
# Save FAISS Index
# ==========================================================

faiss.write_index(

    index,

    str(index_path)

)

print("FAISS Index Saved")

print(index_path)

# CELL 16
# ==========================================================
# Verify Saved Index
# ==========================================================

loaded_index = faiss.read_index(

    str(index_path)

)

print("="*60)

print("Verification")

print("="*60)

print("Vectors :", loaded_index.ntotal)

print("Dimension :", loaded_index.d)

# CELL 17
# ==========================================================
# Save Metadata
# ==========================================================

metadata_output = VECTOR_DB_DIR / "faiss_metadata.parquet"

metadata.to_parquet(

    metadata_output,

    index=False

)

print(metadata_output)

# CELL 18
# ==========================================================
# Validation
# ==========================================================

assert loaded_index.ntotal == len(metadata)

assert loaded_index.d == EMBEDDING_DIMENSION

print("FAISS Validation Passed")

# CELL 19
# ==========================================================
# Load Embedding Model & Chunk Database
# ==========================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(MODEL_NAME)

chunks_df = pd.read_parquet(
    CHUNK_DIR / "chunks.parquet"
)

print("="*60)
print("Embedding Model Loaded")
print("Chunks Loaded :", len(chunks_df))
print("="*60)

# CELL 20
# ==========================================================
# Enterprise Semantic Search
# ==========================================================

def semantic_search(query, top_k=5):

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype(np.float32)

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    retrieved = []

    for score, idx in zip(scores[0], indices[0]):

        meta = metadata.iloc[idx]

        chunk = chunks_df[
            chunks_df["Chunk_ID"] == meta["Chunk_ID"]
        ].iloc[0]

        retrieved.append({

            "Rank": len(retrieved)+1,

            "Score": round(float(score),4),

            "Chunk_ID": meta["Chunk_ID"],

            "Document_ID": meta["Document_ID"],

            "File_Name": meta["File_Name"],

            "Page_Number": meta["Page_Number"],

            "Source": meta["Source"],

            "Chunk_Text": chunk["Chunk_Text"]

        })

    return pd.DataFrame(retrieved)

# CELL 21
# ==========================================================
# Test Query 1
# ==========================================================

query = "How to replace a bearing?"

results = semantic_search(query)

display(results)

# CELL 22
# ==========================================================
# Show Retrieved Chunk Text
# ==========================================================

print("="*80)

print("TOP RETRIEVED CHUNKS")

print("="*80)

for _, row in results.iterrows():

    print(f"\nRank : {row['Rank']}")

    print(f"Similarity : {row['Score']}")

    print(f"File : {row['File_Name']}")

    print(f"Page : {row['Page_Number']}")

    print("-"*80)

    print(row["Chunk_Text"][:800])

    print("\n"+"="*80)

# CELL 23
industrial_queries = [

    "How to replace compressor bearings?",

    "Lockout tagout safety procedure",

    "Preventive maintenance checklist",

    "Electrical motor inspection",

    "Hydraulic pump troubleshooting"

]

for query in industrial_queries:

    print()

    print("="*100)

    print(query)

    print("="*100)

    display(

        semantic_search(

            query,

            top_k=3

        )

    )

# CELL 24
demo_results = {}

for query in industrial_queries:

    demo_results[query] = semantic_search(
        query,
        top_k=3
    ).to_dict(orient="records")

# CELL 25
demo_file = VECTOR_DB_DIR / "sample_search_results.json"

with open(
    demo_file,
    "w"
) as f:

    json.dump(
        demo_results,
        f,
        indent=4
    )

print("Demo Results Saved")

# CELL 26
vector_statistics = {

    "Index Type":"IndexFlatIP",

    "Embedding Dimension":int(index.d),

    "Total Vectors":int(index.ntotal),

    "Metadata Records":int(len(metadata)),

    "Search Model":MODEL_NAME

}

vector_statistics

# CELL 27
statistics_file = VECTOR_DB_DIR/"vector_statistics.json"

with open(
    statistics_file,
    "w"
) as f:

    json.dump(
        vector_statistics,
        f,
        indent=4
    )

print(statistics_file)

# CELL 28
assert demo_file.exists()

assert statistics_file.exists()

assert index.ntotal==len(metadata)

print("="*60)

print("Notebook 06 Validation Passed")

print("="*60)

# CELL 29
print("""

Notebook 06 Completed

Next Notebook

Notebook_07_Gemini_RAG.ipynb

Pipeline

User Question

↓

Semantic Search

↓

Retrieved Chunks

↓

Gemini

↓

Grounded Answer

""")

