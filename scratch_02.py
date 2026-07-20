# CELL 1
pip install PyMuPDF

# CELL 2
# ============================================================
# Imports
# ============================================================

from pathlib import Path
from datetime import datetime

import pandas as pd
import fitz
import json
import logging
import os

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
# ============================================================
# Logging
# ============================================================

logging.basicConfig(

    filename=LOG_DIR/"notebook02_processing.log",

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

    force=True

)

logging.info("Notebook 02 Started")

print("Logger Ready")

# CELL 5
# ============================================================
# Load Inventory
# ============================================================

inventory_path = (

    INVENTORY_DIR/

    "document_inventory.csv"

)

inventory_df = pd.read_csv(

    inventory_path

)

print()

print("="*60)

print("Inventory Loaded")

print("="*60)

print(f"Documents : {len(inventory_df)}")

# CELL 6
inventory_df.head()

# CELL 7
# ============================================================
# Validation
# ============================================================

required_columns=[

"Document_ID",

"File_Name",

"Absolute_Path",

"Extension",

"Department",

"Category"

]

missing=[

c

for c in required_columns

if c not in inventory_df.columns

]

assert len(missing)==0,f"Missing {missing}"

print("Inventory Validation Passed")

# CELL 8
# ============================================================
# Validate File Paths
# ============================================================

inventory_df["Exists"] = inventory_df["Absolute_Path"].apply(

    lambda x: Path(x).exists()

)

print(

inventory_df["Exists"]

.value_counts()

)

# CELL 9
missing_files = inventory_df[

inventory_df["Exists"]==False

]

print(

"Missing Files :",

len(missing_files)

)

# CELL 10
assert inventory_df["Exists"].all()

print("All Documents Found")

# CELL 11
print("="*70)

print("Notebook 02")

print("Enterprise Document Processing")

print("="*70)

print()

print(

inventory_df[

["Department","Category"]

]

.value_counts()

)

# CELL 12
logging.info(

"Inventory Successfully Loaded"

)

print()

print("="*70)

print("MILESTONE 1 COMPLETE")

print("="*70)

# CELL 14
# ============================================================
# Processing Type Detection
# ============================================================

def classify_processing_type(extension: str) -> str:

    extension = extension.lower()

    if extension == ".pdf":
        return "PDF"

    elif extension in [".png", ".jpg", ".jpeg"]:
        return "IMAGE"

    elif extension == ".csv":
        return "CSV"

    elif extension == ".txt":
        return "TEXT"

    return "UNKNOWN"

# CELL 15
# ============================================================
# Assign Processing Type
# ============================================================

inventory_df["Processing_Type"] = (

    inventory_df["Extension"]

    .apply(classify_processing_type)

)

inventory_df[
    [
        "File_Name",
        "Extension",
        "Processing_Type"
    ]
].head()

# CELL 16
print("="*60)

print("Processing Type Distribution")

print("="*60)

display(

inventory_df["Processing_Type"]

.value_counts()

)

# CELL 17
# ============================================================
# PDF Text Detection
# ============================================================

def pdf_contains_text(pdf_path):

    """
    Returns True if PDF has machine-readable text.
    """

    try:

        doc = fitz.open(pdf_path)

        for page in doc:

            text = page.get_text().strip()

            if len(text) > 100:

                doc.close()

                return True

        doc.close()

        return False

    except Exception:

        return False

# CELL 18
# ============================================================
# Initialize Processing Status
# ============================================================

inventory_df["Document_Class"] = "Not Processed"

inventory_df["Requires_OCR"] = False

inventory_df["Processing_Status"] = "Pending"

# CELL 19
# ============================================================
# Classify Every PDF
# ============================================================

pdf_mask = inventory_df["Processing_Type"]=="PDF"

pdfs = inventory_df[pdf_mask]

print("PDF Documents :",len(pdfs))

# CELL 20
from tqdm.auto import tqdm

tqdm.pandas()

# CELL 21
# ============================================================
# Scan PDFs
# ============================================================

def classify_pdf(path):

    if pdf_contains_text(path):

        return "TEXT_PDF"

    return "SCANNED_PDF"

inventory_df.loc[

pdf_mask,

"Document_Class"

]=inventory_df.loc[

pdf_mask,

"Absolute_Path"

].progress_apply(

classify_pdf

)

# CELL 22
inventory_df.loc[

inventory_df["Processing_Type"]=="IMAGE",

"Document_Class"

]="IMAGE"

# CELL 23
inventory_df.loc[

inventory_df["Processing_Type"]=="CSV",

"Document_Class"

]="CSV"

# CELL 24
inventory_df.loc[

inventory_df["Processing_Type"]=="TEXT",

"Document_Class"

]="TEXT"

# CELL 25
inventory_df["Requires_OCR"]=(

inventory_df["Document_Class"]

.isin(

["SCANNED_PDF","IMAGE"]

)

)

# CELL 26
display(

inventory_df[

[

"File_Name",

"Processing_Type",

"Document_Class",

"Requires_OCR"

]

].head(20)

)

# CELL 27
print("="*70)

print("Document Classes")

print("="*70)

display(

inventory_df["Document_Class"]

.value_counts()

)

# CELL 28
print("="*60)

print("OCR Queue Size")

print("="*60)

print(

inventory_df["Requires_OCR"]

.value_counts()

)

# CELL 29
ocr_queue = inventory_df[

inventory_df["Requires_OCR"]

].copy()

display(

ocr_queue.head()

)

# CELL 30
assert len(inventory_df)>0

assert inventory_df["Document_Class"].notna().all()

assert inventory_df["Requires_OCR"].notna().all()

print("Classification Validation Passed")

# CELL 31
logging.info("Document Classification Completed")

print()

print("="*70)

print("MILESTONE 2 COMPLETED")

print("="*70)

# CELL 33
# ============================================================
# Text Extraction Function
# ============================================================

def extract_pdf_text(pdf_path: str):
    """
    Extract text page-by-page from a machine-readable PDF.

    Returns
    -------
    dict
    """

    pages = []

    total_characters = 0

    try:

        pdf = fitz.open(pdf_path)

        for page_number, page in enumerate(pdf, start=1):

            text = page.get_text("text")

            pages.append({

                "Page_Number": page_number,

                "Text": text

            })

            total_characters += len(text)

        pdf.close()

        return {

            "Success": True,

            "Pages": len(pages),

            "Characters": total_characters,

            "Content": pages

        }

    except Exception as e:

        return {

            "Success": False,

            "Pages": 0,

            "Characters": 0,

            "Content": [],

            "Error": str(e)

        }

# CELL 34
# ============================================================
# Select Readable PDFs
# ============================================================

text_pdf_df = inventory_df[

    inventory_df["Document_Class"]=="TEXT_PDF"

].copy()

print()

print("="*60)

print("Readable PDFs")

print("="*60)

print(len(text_pdf_df))

# CELL 35
from tqdm.auto import tqdm

tqdm.pandas()

# CELL 36
# ============================================================
# Extract Text
# ============================================================

text_pdf_df["Extraction_Result"] = (

    text_pdf_df["Absolute_Path"]

    .progress_apply(

        extract_pdf_text

    )

)

# CELL 37
# ============================================================
# Extraction Status
# ============================================================

text_pdf_df["Extraction_Success"] = (

    text_pdf_df["Extraction_Result"]

    .apply(

        lambda x: x["Success"]

    )

)

text_pdf_df["Total_Pages"] = (

    text_pdf_df["Extraction_Result"]

    .apply(

        lambda x: x["Pages"]

    )

)

text_pdf_df["Characters"] = (

    text_pdf_df["Extraction_Result"]

    .apply(

        lambda x: x["Characters"]

    )

)

# CELL 38
display(

text_pdf_df[

[

"Document_ID",

"File_Name",

"Extraction_Success",

"Total_Pages",

"Characters"

]

]
)

# CELL 39
# ============================================================
# Build Text Corpus
# ============================================================

text_records = []

for _, row in text_pdf_df.iterrows():

    pages = row["Extraction_Result"]["Content"]

    for page in pages:

        text_records.append({

            "Document_ID": row["Document_ID"],

            "File_Name": row["File_Name"],

            "Page_Number": page["Page_Number"],

            "Text": page["Text"]

        })

text_corpus = pd.DataFrame(text_records)

text_corpus.head()

# CELL 40
print()

print("="*70)

print("TEXT CORPUS")

print("="*70)

print("Pages :",len(text_corpus))

print("Documents :",text_corpus["Document_ID"].nunique())

# CELL 41
# ============================================================
# Processing Errors
# ============================================================

processing_errors = text_pdf_df[

text_pdf_df["Extraction_Success"]==False

]

processing_errors

# CELL 42
# ============================================================
# Preview Extracted Text
# ============================================================

display(

text_corpus.head()

)

# CELL 43
# ============================================================
# Export Text Corpus
# ============================================================

text_output = (

OUTPUT_DIR/

"text_documents.parquet"

)

text_corpus.to_parquet(

text_output,

index=False

)

print(text_output)

# CELL 44
# ============================================================
# Export Processed Documents
# ============================================================

processed_output=(

OUTPUT_DIR/

"processed_documents.parquet"

)

text_pdf_df.drop(

columns=["Extraction_Result"]

).to_parquet(

processed_output,

index=False

)

print(processed_output)

# CELL 45
# ============================================================
# Export Errors
# ============================================================

error_output=(

OUTPUT_DIR/

"processing_errors.csv"

)

processing_errors.to_csv(

error_output,

index=False

)

print(error_output)

# CELL 46
# ============================================================
# Validation
# ============================================================

assert processed_output.exists()

assert text_output.exists()

assert error_output.exists()

print("Text Extraction Validation Passed")

# CELL 47
logging.info(

"Text Extraction Completed"

)

print()

print("="*70)

print("MILESTONE 3 COMPLETED")

print("="*70)

# CELL 49
# ============================================================
# Prepare OCR Queue
# ============================================================

ocr_queue = inventory_df[
    inventory_df["Requires_OCR"] == True
].copy()

ocr_queue = ocr_queue[
    [
        "Document_ID",
        "File_Name",
        "Absolute_Path",
        "Department",
        "Category",
        "Document_Class"
    ]
]

print("=" * 60)
print("OCR Queue")
print("=" * 60)
print(f"Documents requiring OCR : {len(ocr_queue)}")

display(ocr_queue.head())

# CELL 50
# ============================================================
# Export OCR Queue
# ============================================================

ocr_queue_output = OUTPUT_DIR / "ocr_queue.csv"

ocr_queue.to_csv(
    ocr_queue_output,
    index=False
)

print(f"OCR Queue saved to:\n{ocr_queue_output}")

# CELL 51
# ============================================================
# Processing Statistics
# ============================================================

processing_statistics = {

    "Total Documents":
        int(len(inventory_df)),

    "Readable PDFs":
        int((inventory_df["Document_Class"]=="TEXT_PDF").sum()),

    "Scanned PDFs":
        int((inventory_df["Document_Class"]=="SCANNED_PDF").sum()),

    "Images":
        int((inventory_df["Document_Class"]=="IMAGE").sum()),

    "CSV Files":
        int((inventory_df["Document_Class"]=="CSV").sum()),

    "TXT Files":
        int((inventory_df["Document_Class"]=="TEXT").sum()),

    "OCR Queue":
        int(len(ocr_queue)),

    "Successfully Processed PDFs":
        int(text_pdf_df["Extraction_Success"].sum()),

    "Failed PDF Processing":
        int((~text_pdf_df["Extraction_Success"]).sum()),

    "Total Pages Extracted":
        int(text_pdf_df["Total_Pages"].sum()),

    "Total Characters":
        int(text_pdf_df["Characters"].sum())
}

processing_statistics

# CELL 52
# ============================================================
# Export Processing Statistics
# ============================================================

statistics_output = OUTPUT_DIR / "processing_statistics.json"

with open(statistics_output, "w") as f:
    json.dump(processing_statistics, f, indent=4)

print(f"Saved:\n{statistics_output}")

# CELL 53
# ============================================================
# Processing Dashboard
# ============================================================

print("=" * 70)
print("ENTERPRISE DOCUMENT PROCESSING SUMMARY")
print("=" * 70)

for key, value in processing_statistics.items():
    print(f"{key:<35}: {value}")

print("=" * 70)

# CELL 54
# ============================================================
# Verify Outputs
# ============================================================

outputs = [

    processed_output,

    text_output,

    error_output,

    ocr_queue_output,

    statistics_output

]

print("=" * 60)
print("OUTPUT VERIFICATION")
print("=" * 60)

for output in outputs:
    print(f"{output.name:<35} : {output.exists()}")

# CELL 55
# ============================================================
# Final Validation
# ============================================================

assert processed_output.exists()
assert text_output.exists()
assert error_output.exists()
assert ocr_queue_output.exists()
assert statistics_output.exists()

assert len(inventory_df) > 0
assert len(text_pdf_df) >= 0
assert len(ocr_queue) >= 0

print("All validation checks passed.")

# CELL 56
# ============================================================
# Output Directory Preview
# ============================================================

import os

print("=" * 70)
print("GENERATED FILES")
print("=" * 70)

for file in sorted(os.listdir(OUTPUT_DIR)):
    print(file)

# CELL 57
# ============================================================
# Notebook Completion
# ============================================================

logging.info("=" * 80)
logging.info("Notebook 02 Completed Successfully")
logging.info("=" * 80)

print()
print("=" * 80)
print("NOTEBOOK 02 COMPLETED SUCCESSFULLY")
print("=" * 80)

# CELL 58
print("""
Notebook 03 Input

processed_documents.parquet
text_documents.parquet
ocr_queue.csv
processing_statistics.json

Next:
Enterprise OCR Pipeline
""")

# CELL 59
import os

print("Inventory Files:")
print(os.listdir(INVENTORY_DIR))

print("\nProcessed Files:")
print(os.listdir(OUTPUT_DIR))
