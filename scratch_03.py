# CELL 1
# ==========================================================
# Install Dependencies
# ==========================================================

!pip -q install easyocr pymupdf pillow tqdm

# CELL 2
# ==========================================================
# Imports
# ==========================================================

from pathlib import Path
from tqdm.auto import tqdm

import pandas as pd
import fitz
import easyocr
import cv2
import numpy as np
import json
import logging
import os

from PIL import Image

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
# Logger
# ==========================================================

logging.basicConfig(

filename=LOG_DIR/"notebook03_ocr.log",

level=logging.INFO,

format="%(asctime)s | %(levelname)s | %(message)s",

force=True

)

logging.info("Notebook03 Started")

print("Logger Ready")

# CELL 5
# ==========================================================
# Load OCR Queue
# ==========================================================

ocr_queue = pd.read_csv(

PROCESSED_DIR/

"ocr_queue.csv"

)

print()

print("="*60)

print("OCR Queue Loaded")

print("="*60)

print()

print("Documents :",len(ocr_queue))

# CELL 6
# ==========================================================
# Load Native Text Corpus
# ==========================================================

text_corpus = pd.read_parquet(

PROCESSED_DIR/

"text_documents.parquet"

)

print()

print("Native Pages :",len(text_corpus))

# CELL 7
display(

ocr_queue.head()

)

# CELL 8
# ==========================================================
# Initialize EasyOCR
# ==========================================================

reader = easyocr.Reader(

['en'],

gpu=False

)

print("OCR Engine Ready")

# CELL 9
# ==========================================================
# Supported OCR Formats
# ==========================================================

IMAGE_EXTENSIONS = [

".jpg",

".jpeg",

".png"

]

PDF_EXTENSION = ".pdf"

# CELL 10
print("="*60)

print("OCR Pipeline")

print("="*60)

print()

print("Queue :",len(ocr_queue))

print("Native Corpus :",len(text_corpus))

# CELL 11
assert len(ocr_queue)>=0

assert len(text_corpus)>0

print("Validation Passed")

# CELL 12
def preprocess_image(image_path):

    image = cv2.imread(str(image_path))

    if image is None:
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    return gray

# CELL 13
# ==========================================================
# Robust Image OCR
# ==========================================================

def extract_text_from_image(image_path):
    try:
        image = preprocess_image(image_path)
        if image is None:
            return {
                "Success": False,
                "Text": "",
                "Confidence": 0,
                "Error": f"Image preprocessing returned None for {image_path}"
            }

        results = reader.readtext(
            image,
            detail=1
        )

        extracted_text = []
        confidence_scores = []

        for item in results:
            try:
                # Expecting (bbox, text, prob)
                if not isinstance(item, (list, tuple)) or len(item) != 3:
                    logging.warning(f"Skipping malformed EasyOCR result item (not list/tuple or wrong length): {item}")
                    continue

                bbox, text_content, confidence_score = item

                text = str(text_content).strip()
                conf = float(confidence_score)

                if len(text) == 0:
                    continue

                extracted_text.append(text)
                confidence_scores.append(conf)

            except (TypeError, ValueError, IndexError) as item_error:
                logging.error(f"Error processing individual EasyOCR result item {item}: {item_error}")
                continue # Skip this problematic item and continue with others

        final_text = "\n".join(extracted_text)
        avg_confidence = (
            round(np.mean(confidence_scores),3)
            if confidence_scores else 0
        )

        return {
            "Success": True,
            "Text": final_text,
            "Confidence": avg_confidence
        }

    except Exception as e:
        return {
            "Success": False,
            "Text": "",
            "Confidence": 0,
            "Error": str(e)
        }

# CELL 14
sample = reader.readtext(
    str(ocr_queue.iloc[0]["Absolute_Path"]),
    detail=1
)

print(sample)

# CELL 15
# ==========================================================
# OCR Function for Scanned PDFs
# ==========================================================

def extract_text_from_pdf(pdf_path):

    pages=[]

    try:

        pdf=fitz.open(pdf_path)

        for page in pdf:

            pix=page.get_pixmap(dpi=250)

            image=np.frombuffer(

                pix.samples,

                dtype=np.uint8

            ).reshape(

                pix.height,

                pix.width,

                pix.n

            )

            result=reader.readtext(

                image,

                detail=0,

                paragraph=True

            )

            pages.append(

                "\n".join(result)

            )

        pdf.close()

        return {

            "Success":True,

            "Text":"\n".join(pages)

        }

    except Exception as e:

        return {

            "Success":False,

            "Text":"",

            "Error":str(e)

        }

# CELL 16
# ==========================================================
# OCR Entire Queue
# ==========================================================

ocr_results=[]

errors=[]

print("Running OCR...")

# CELL 17
from tqdm.auto import tqdm

for _,row in tqdm(

    ocr_queue.iterrows(),

    total=len(ocr_queue)

):

    path=Path(

        row["Absolute_Path"]

    )

    extension=path.suffix.lower()

    if extension in IMAGE_EXTENSIONS:

        output=extract_text_from_image(path)

    elif extension==".pdf":

        output=extract_text_from_pdf(path)

    else:

        continue

    if output["Success"]:

        ocr_results.append({

            "Document_ID":row["Document_ID"],

            "File_Name":row["File_Name"],

            "Department":row["Department"],

            "Category":row["Category"],

            "OCR_Text":output["Text"],

            "Confidence":

                output.get(

                    "Confidence",

                    None

                )

        })

    else:

        errors.append({

            "Document_ID":row["Document_ID"],

            "File_Name":row["File_Name"],

            "Error":output["Error"]

        })

# CELL 18
ocr_df=pd.DataFrame(

ocr_results

)

display(

ocr_df.head()

)

# CELL 19
errors_df=pd.DataFrame(

errors

)

print()

print("="*60)

print("OCR Completed")

print("="*60)

print()

print("Success :",len(ocr_df))

print("Errors :",len(errors_df))

# CELL 20
# ==========================================================
# Basic Cleaning
# ==========================================================

def clean_text(text):

    if pd.isna(text):

        return ""

    text=text.replace("\n\n","\n")

    text=text.replace("\t"," ")

    text=text.replace("  "," ")

    return text.strip()

# CELL 22
# Apply the clean_text function to the OCR_Text column
ocr_df["OCR_Text"] = ocr_df["OCR_Text"].apply(clean_text)

# Prepare ocr_df for merging by selecting relevant columns and renaming
ocr_corpus_df = ocr_df[[
    "Document_ID",
    "File_Name",
    "OCR_Text"
]].copy()
ocr_corpus_df.rename(
    columns={"OCR_Text": "text"},
    inplace=True
)
ocr_corpus_df["source"] = "OCR"
ocr_corpus_df["page_number"] = None # OCR text is per document, not per page

# CELL 23
# Prepare text_corpus for merging by selecting relevant columns and renaming
print("text_corpus columns before selection:", text_corpus.columns)
native_corpus_df = text_corpus[[
    "Document_ID",
    "File_Name",
    "Page_Number",
    "Text"
]].copy()
native_corpus_df.rename(
    columns={"Text": "text"},
    inplace=True
)
native_corpus_df["source"] = "Native PDF"

# CELL 24
# Concatenate both dataframes to form the unified corpus
merged_corpus = pd.concat(
    [ocr_corpus_df, native_corpus_df],
    ignore_index=True
)

print("Unified Corpus Created!")
display(merged_corpus.head())

# CELL 25
errors_df.head(20)

# CELL 26
display(errors_df)

# CELL 27
print(errors_df.shape)

# CELL 28
errors_df = pd.DataFrame(
    errors,
    columns=[
        "Document_ID",
        "File_Name",
        "Error"
    ]
)

# CELL 29
print("OCR Success:", len(ocr_df))
print("OCR Errors :", len(errors_df))
print("Merged Corpus:", len(merged_corpus))

# CELL 30
print(len(merged_corpus))

# CELL 31
# ==========================================================
# Export OCR Text
# ==========================================================

ocr_output = OCR_DIR / "ocr_text.parquet"

ocr_df.to_parquet(
    ocr_output,
    index=False
)

print(f"OCR Text Saved:\n{ocr_output}")

# CELL 32
# ==========================================================
# Export Merged Corpus
# ==========================================================

merged_output = OCR_DIR / "merged_text_corpus.parquet"

merged_corpus.to_parquet(
    merged_output,
    index=False
)

print(f"Merged Corpus Saved:\n{merged_output}")

# CELL 33
# ==========================================================
# Export OCR Errors
# ==========================================================

error_output = OCR_DIR / "ocr_errors.csv"

errors_df.to_csv(
    error_output,
    index=False
)

print(f"Errors Saved:\n{error_output}")

# CELL 34
# ==========================================================
# OCR Statistics
# ==========================================================

ocr_statistics = {

    "Total OCR Documents": int(len(ocr_queue)),

    "OCR Success": int(len(ocr_df)),

    "OCR Errors": int(len(errors_df)),

    "Merged Corpus Records": int(len(merged_corpus)),

    "Unique Documents": int(
        merged_corpus["Document_ID"].nunique()
    ),

    "OCR Images": int(
        (ocr_queue["Document_Class"]=="IMAGE").sum()
    ),

    "Scanned PDFs": int(
        (ocr_queue["Document_Class"]=="SCANNED_PDF").sum()
    )

}

ocr_statistics

# CELL 35
# ==========================================================
# Export Statistics
# ==========================================================

statistics_output = OCR_DIR / "ocr_statistics.json"

with open(statistics_output,"w") as f:

    json.dump(

        ocr_statistics,

        f,

        indent=4

    )

print(statistics_output)

# CELL 36
# ==========================================================
# Statistics Dashboard
# ==========================================================

print("="*70)

print("OCR PIPELINE SUMMARY")

print("="*70)

for k,v in ocr_statistics.items():

    print(f"{k:<30}: {v}")

print("="*70)

# CELL 37
# ==========================================================
# Output Verification
# ==========================================================

outputs=[

ocr_output,

merged_output,

error_output,

statistics_output

]

print("="*60)

print("Generated Files")

print("="*60)

for file in outputs:

    print(

        f"{file.name:<35}",

        file.exists()

    )

# CELL 38
# ==========================================================
# Final Validation
# ==========================================================

assert ocr_output.exists()

assert merged_output.exists()

assert error_output.exists()

assert statistics_output.exists()

assert len(merged_corpus)>0

assert len(ocr_df)>0

print("Notebook 03 Validation Passed")

# CELL 39
# ==========================================================
# Sample OCR Output
# ==========================================================

display(

ocr_df[

[

"Document_ID",

"File_Name",

"Confidence",

"OCR_Text"

]

].head()

)

# CELL 40
# ==========================================================
# Sample Merged Corpus
# ==========================================================

display(

merged_corpus.head(10)

)

# CELL 41
# ==========================================================
# Notebook Completion
# ==========================================================

logging.info("="*80)

logging.info("Notebook 03 Completed Successfully")

logging.info("="*80)

print()

print("="*80)

print("NOTEBOOK 03 COMPLETED SUCCESSFULLY")

print("="*80)

# CELL 42
print("""

Next Notebook

Notebook 04

Semantic Chunking
+
Embeddings
+
FAISS Index

Input

merged_text_corpus.parquet

Output

chunks.parquet

embeddings.npy

faiss.index

""")

