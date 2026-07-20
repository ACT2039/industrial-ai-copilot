# CELL 1
# ==========================================================
# Install Libraries
# ==========================================================

!pip -q install sentence-transformers

# CELL 2
# ==========================================================
# Imports
# ==========================================================

from pathlib import Path

import numpy as np
import pandas as pd
import json
import logging

from sentence_transformers import SentenceTransformer

print("Libraries Imported")

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
# Configure Logger
# ==========================================================

logging.basicConfig(

    filename=LOG_DIR/"notebook05_embeddings.log",

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

    force=True

)

logging.info("Notebook 05 Started")

print("Logger Ready")

# CELL 5
# ==========================================================
# Load Chunks
# ==========================================================

chunk_path = CHUNK_DIR / "chunks.parquet"

chunks_df = pd.read_parquet(chunk_path)

print("="*60)
print("Chunks Loaded")
print("="*60)

print("Total Chunks :", len(chunks_df))

# CELL 6
display(

chunks_df.head()

)

# CELL 7
# ==========================================================
# Validate Input
# ==========================================================

required_columns = [

    "Chunk_ID",

    "Document_ID",

    "Chunk_Text"

]

missing = [

    col

    for col in required_columns

    if col not in chunks_df.columns

]

assert len(missing) == 0, f"Missing Columns: {missing}"

assert len(chunks_df) > 0

print("Validation Passed")

# CELL 8
print("="*60)

print("Dataset Summary")

print("="*60)

print("Chunks :", len(chunks_df))

print("Unique Documents :", chunks_df["Document_ID"].nunique())

# CELL 9
logging.info("Chunk Dataset Successfully Loaded")

print()

print("="*70)

print("MILESTONE 1 COMPLETED")

print("="*70)

# CELL 10
# ==========================================================
# Create Batch Directory
# ==========================================================

BATCH_DIR = EMBEDDING_DIR / "batches"

BATCH_DIR.mkdir(
    parents=True,
    exist_ok=True
)

print(BATCH_DIR)

# CELL 11
# ==========================================================
# Load Model
# ==========================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(
    MODEL_NAME
)

EMBED_DIM = embedding_model.get_sentence_embedding_dimension()

print("Embedding Dimension :", EMBED_DIM)

# CELL 12
# ==========================================================
# Prepare Text
# ==========================================================

texts = (

    chunks_df["Chunk_Text"]

    .fillna("")

    .astype(str)

    .tolist()

)

print("Total Texts :", len(texts))

# CELL 13
# ==========================================================
# Batch Configuration
# ==========================================================

BATCH_SIZE = 1000

TOTAL_BATCHES = (

    len(texts)

    + BATCH_SIZE - 1

)//BATCH_SIZE

print("Total Batches :", TOTAL_BATCHES)

# CELL 14
# ==========================================================
# Resume Existing Batches
# ==========================================================

existing_batches = sorted(

    BATCH_DIR.glob(

        "batch_*.npy"

    )

)

completed = len(existing_batches)

print("Completed Batches :", completed)

print("Remaining :", TOTAL_BATCHES-completed)

# CELL 15
# ==========================================================
# Generate Embeddings Batch by Batch
# ==========================================================

from tqdm.auto import tqdm

for batch_idx in tqdm(range(completed, TOTAL_BATCHES)):

    start = batch_idx * BATCH_SIZE
    end = min(start + BATCH_SIZE, len(texts))

    batch_texts = texts[start:end]

    batch_embeddings = embedding_model.encode(

        batch_texts,

        batch_size=64,

        show_progress_bar=False,

        convert_to_numpy=True,

        normalize_embeddings=True

    )

    batch_file = BATCH_DIR / f"batch_{batch_idx:04d}.npy"

    np.save(batch_file, batch_embeddings)

    print(f"✅ Saved {batch_file.name}")

# CELL 16
# ==========================================================
# Verify Generated Batch Files
# ==========================================================

batch_files = sorted(BATCH_DIR.glob("batch_*.npy"))

print("="*60)
print("Batch Verification")
print("="*60)

print("Expected Batches :", TOTAL_BATCHES)
print("Generated Batches:", len(batch_files))

# CELL 17
# ==========================================================
# Merge All Batch Files
# ==========================================================

embedding_list = []

for file in batch_files:

    embedding_list.append(

        np.load(file)

    )

embeddings = np.vstack(embedding_list)

print("Merged Shape :", embeddings.shape)

# CELL 18
# ==========================================================
# Embedding Validation
# ==========================================================

assert embeddings.shape[0] == len(chunks_df)

assert embeddings.shape[1] == EMBED_DIM

print("Embedding Validation Passed")

# CELL 19
# ==========================================================
# Add Embedding Index
# ==========================================================

chunks_df["Embedding_Index"] = np.arange(

    len(chunks_df)

)

display(chunks_df.head())

# CELL 20
# ==========================================================
# Save Final Embedding Matrix
# ==========================================================

embedding_output = EMBEDDING_DIR / "embeddings.npy"

np.save(

    embedding_output,

    embeddings

)

print(embedding_output)

# CELL 21
# ==========================================================
# Save Embedding Metadata
# ==========================================================

embedding_metadata = chunks_df[

    [

        "Embedding_Index",

        "Chunk_ID",

        "Document_ID",

        "File_Name",

        "Page_Number",

        "Source",

        "Chunk_Number",

        "Characters",

        "Words"

    ]

]

metadata_output = EMBEDDING_DIR / "embedding_metadata.parquet"

embedding_metadata.to_parquet(

    metadata_output,

    index=False

)

print(metadata_output)

# CELL 22
# ==========================================================
# Save Progress File
# ==========================================================

progress = {

    "completed_batches": len(batch_files),

    "total_batches": TOTAL_BATCHES,

    "batch_size": BATCH_SIZE,

    "total_embeddings": len(chunks_df),

    "model": MODEL_NAME

}

with open(

    EMBEDDING_DIR / "progress.json",

    "w"

) as f:

    json.dump(

        progress,

        f,

        indent=4

    )

print("Progress Saved")

# CELL 23
# ==========================================================
# Embedding Statistics
# ==========================================================

embedding_statistics = {

    "Model": MODEL_NAME,

    "Embedding Dimension": EMBED_DIM,

    "Total Chunks": len(chunks_df),

    "Embedding Shape": list(embeddings.shape),

    "Total Batches": TOTAL_BATCHES,

    "Completed Batches": len(batch_files)

}

embedding_statistics

# CELL 24
# ==========================================================
# Save Statistics
# ==========================================================

statistics_output = EMBEDDING_DIR / "embedding_statistics.json"

with open(

    statistics_output,

    "w"

) as f:

    json.dump(

        embedding_statistics,

        f,

        indent=4

    )

print(statistics_output)

# CELL 25
# ==========================================================
# Final Validation
# ==========================================================

assert embedding_output.exists()

assert metadata_output.exists()

assert statistics_output.exists()

assert (EMBEDDING_DIR / "progress.json").exists()

print("="*60)
print("Notebook 05 Completed Successfully")
print("="*60)

