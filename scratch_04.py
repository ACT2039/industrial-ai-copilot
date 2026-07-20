# CELL 1
# ==========================================================
# Install Required Libraries
# ==========================================================

!pip -q install pandas pyarrow tqdm

# CELL 2
# ==========================================================
# Imports
# ==========================================================

from pathlib import Path
from tqdm.auto import tqdm

import pandas as pd
import json
import logging
import re
import os

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

    filename=LOG_DIR/"notebook04_chunking.log",

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

    force=True

)

logging.info("Notebook 04 Started")

print("Logger Ready")

# CELL 5
# ==========================================================
# Load Merged Corpus
# ==========================================================

merged_path = OCR_DIR / "merged_text_corpus.parquet"

merged_corpus = pd.read_parquet(merged_path)

print("="*60)
print("Merged Corpus Loaded")
print("="*60)

print("Total Records :", len(merged_corpus))

# CELL 6
if 'text' in merged_corpus.columns:
    merged_corpus.rename(columns={'text': 'Content'}, inplace=True)
    logging.info("Renamed 'text' to 'Content' in merged_corpus.")
else:
    logging.warning("'text' column not found for renaming.")

# Add 'Source' column with a default value if it doesn't exist
if 'Source' not in merged_corpus.columns:
    merged_corpus['Source'] = merged_corpus['File_Name'] # Using 'File_Name' as a placeholder for Source
    logging.info("Added 'Source' column to merged_corpus using 'File_Name' as placeholder.")
else:
    logging.info("'Source' column already exists.")

print("DataFrame prepared for validation.")
logging.info("DataFrame columns adjusted for validation.")

# CELL 7
display(merged_corpus.head())

# CELL 8
display(merged_corpus.head())

# CELL 9
# ==========================================================
# Validate Required Columns
# ==========================================================

# Ensure 'Content' column is present by renaming 'text' if it exists
if 'text' in merged_corpus.columns and 'Content' not in merged_corpus.columns:
    merged_corpus.rename(columns={'text': 'Content'}, inplace=True)
    logging.info("Renamed 'text' to 'Content' before validation in QoEXFR6oa4cI.")
elif 'text' not in merged_corpus.columns and 'Content' not in merged_corpus.columns:
    logging.warning("'text' or 'Content' column not found before validation.")

# Ensure 'Source' column is present
if 'Source' not in merged_corpus.columns:
    merged_corpus['Source'] = merged_corpus['File_Name'] # Using 'File_Name' as a placeholder for Source
    logging.info("Added 'Source' column before validation in QoEXFR6oa4cI.")


required_columns = [
    "Document_ID",
    "File_Name",
    "Page_Number",
    "Content",
    "Source"
]

missing = [
    col
    for col in required_columns
    if col not in merged_corpus.columns
]

assert len(missing) == 0, f"Missing Columns : {missing}"

print("Validation Passed")
logging.info("Column validation passed.")

# CELL 10
print("="*60)

print("Corpus Statistics")

print("="*60)

print("Documents :", merged_corpus["Document_ID"].nunique())

print("Pages :", len(merged_corpus))

print("Sources")

display(

    merged_corpus["Source"]

    .value_counts()

)

# CELL 11
logging.info("Corpus Successfully Loaded")

print()

print("="*70)

print("MILESTONE 1 COMPLETED")

print("="*70)

# CELL 12
# ==========================================================
# Text Cleaning Function
# ==========================================================

def clean_text(text):

    if pd.isna(text):
        return ""

    text = str(text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    # Remove repeated newlines
    text = re.sub(r"\n+", "\n", text)

    # Remove tabs
    text = text.replace("\t", " ")

    # Remove NULL characters
    text = text.replace("\x00", "")

    return text.strip()

# CELL 13
merged_corpus["Content"] = merged_corpus["Content"].apply(clean_text)

display(merged_corpus.head())

# CELL 14
print("="*60)
print("Cleaning Completed")
print("="*60)

print("Remaining Empty Documents :")

print((merged_corpus["Content"]=="").sum())

# CELL 15
# ==========================================================
# Chunk Parameters
# ==========================================================

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 200

# CELL 16
# ==========================================================
# Recursive Chunk Function
# ==========================================================

def split_into_chunks(text):

    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk = text[start:end]

        chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks

# CELL 17
sample = merged_corpus.iloc[0]["Content"]

sample_chunks = split_into_chunks(sample)

print("Chunks Generated :", len(sample_chunks))

# CELL 18
print(sample_chunks[0][:500])

# CELL 19
chunk_records = []

chunk_counter = 1

# CELL 20
from tqdm.auto import tqdm

for _, row in tqdm(

    merged_corpus.iterrows(),

    total=len(merged_corpus)

):

    chunks = split_into_chunks(

        row["Content"]

    )

    for number, chunk in enumerate(chunks, start=1):

        chunk_records.append({

            "Chunk_ID":f"CHUNK{chunk_counter:06d}",

            "Document_ID":row["Document_ID"],

            "File_Name":row["File_Name"],

            "Page_Number":row["Page_Number"],

            "Source":row["Source"],

            "Chunk_Number":number,

            "Chunk_Text":chunk,

            "Characters":len(chunk),

            "Words":len(chunk.split())

        })

        chunk_counter += 1

# CELL 21
chunks_df = pd.DataFrame(

chunk_records

)

display(

chunks_df.head()

)

# CELL 22
print("="*70)

print("Chunk Statistics")

print("="*70)

print("Chunks :",len(chunks_df))

print("Documents :",chunks_df["Document_ID"].nunique())

print("Average Words :",round(chunks_df["Words"].mean(),1))

# CELL 23
assert len(chunks_df)>0

assert chunks_df["Chunk_ID"].is_unique

print("Chunk Validation Passed")

# CELL 24
# ==========================================================
# Chunk Metadata
# ==========================================================

chunk_metadata = chunks_df[

    [

        "Chunk_ID",

        "Document_ID",

        "File_Name",

        "Page_Number",

        "Source",

        "Chunk_Number",

        "Characters",

        "Words"

    ]

].copy()

display(chunk_metadata.head())

# CELL 25
print("="*70)

print("Chunk Metadata")

print("="*70)

print("Total Chunks :", len(chunk_metadata))

print("Unique Documents :", chunk_metadata["Document_ID"].nunique())

# CELL 26
# ==========================================================
# Chunk Statistics
# ==========================================================

chunk_statistics = {

    "Total Chunks":

        int(len(chunks_df)),

    "Unique Documents":

        int(chunks_df["Document_ID"].nunique()),

    "Average Characters":

        round(chunks_df["Characters"].mean(),2),

    "Average Words":

        round(chunks_df["Words"].mean(),2),

    "Maximum Characters":

        int(chunks_df["Characters"].max()),

    "Minimum Characters":

        int(chunks_df["Characters"].min())

}

chunk_statistics

# CELL 27
print("="*70)

print("CHUNKING SUMMARY")

print("="*70)

for key,value in chunk_statistics.items():

    print(f"{key:<30}: {value}")

print("="*70)

# CELL 28
# ==========================================================
# Export Chunks
# ==========================================================

chunks_output = CHUNK_DIR / "chunks.parquet"

chunks_df.to_parquet(

    chunks_output,

    index=False

)

print(chunks_output)

# CELL 29
# ==========================================================
# Export Chunk Metadata
# ==========================================================

metadata_output = CHUNK_DIR / "chunk_metadata.parquet"

chunk_metadata.to_parquet(

    metadata_output,

    index=False

)

print(metadata_output)

# CELL 30
# ==========================================================
# Export Statistics
# ==========================================================

statistics_output = CHUNK_DIR / "chunk_statistics.json"

with open(

    statistics_output,

    "w"

) as f:

    json.dump(

        chunk_statistics,

        f,

        indent=4

    )

print(statistics_output)

# CELL 31
# ==========================================================
# Verify Outputs
# ==========================================================

outputs = [

    chunks_output,

    metadata_output,

    statistics_output

]

print("="*60)

print("Generated Files")

print("="*60)

for file in outputs:

    print(f"{file.name:<35} : {file.exists()}")

# CELL 32
# ==========================================================
# Final Validation
# ==========================================================

assert chunks_output.exists()

assert metadata_output.exists()

assert statistics_output.exists()

assert chunks_df["Chunk_ID"].is_unique

assert len(chunks_df) > 0

assert chunks_df["Chunk_Text"].str.len().gt(0).all()

print("Notebook 04 Validation Passed")

# CELL 33
# ==========================================================
# Preview Final Chunks
# ==========================================================

display(

    chunks_df.head(10)

)

# CELL 34
# ==========================================================
# Notebook Completion
# ==========================================================

logging.info("="*80)
logging.info("Notebook 04 Completed Successfully")
logging.info("="*80)

print()

print("="*80)

print("NOTEBOOK 04 COMPLETED SUCCESSFULLY")

print("="*80)

# CELL 35
print("""

Notebook 05

Embedding Generation

Input

chunks.parquet

Output

embeddings.npy

embedding_metadata.parquet

""")

# CELL 36
print("Total Chunks:", len(chunks_df))

print("Average Words:", round(chunks_df["Words"].mean(), 2))

print("Maximum Words:", chunks_df["Words"].max())

print("Minimum Words:", chunks_df["Words"].min())

# CELL 37
# ==========================================================
# Remove Very Small Chunks
# ==========================================================

MIN_WORDS = 30

before = len(chunks_df)

chunks_df = chunks_df[
    chunks_df["Words"] >= MIN_WORDS
].reset_index(drop=True)

after = len(chunks_df)

print("=" * 60)
print("Chunk Filtering")
print("=" * 60)

print(f"Before : {before}")
print(f"After  : {after}")
print(f"Removed: {before-after}")

# CELL 38
print("="*60)

print("Filtered Statistics")

print("="*60)

print("Chunks :",len(chunks_df))

print("Average Words :",round(chunks_df["Words"].mean(),2))

print("Minimum Words :",chunks_df["Words"].min())

print("Maximum Words :",chunks_df["Words"].max())

