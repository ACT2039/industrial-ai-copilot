"""
Project Configuration

Author: Charan Teja Arangi
"""

from pathlib import Path

# Dynamically resolve project root: src/core/config.py -> src/core -> src -> root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CHUNK_DIR = DATA_DIR / "chunks"
EMBEDDING_DIR = DATA_DIR / "embeddings"
VECTOR_DB_DIR = DATA_DIR / "vector_db"
KG_DIR = DATA_DIR / "knowledge_graph"
INVENTORY_DIR = DATA_DIR / "inventory"
LOG_DIR = PROJECT_ROOT / "logs"
OCR_DIR = DATA_DIR / "ocr"
OCR_DIR.mkdir(parents=True, exist_ok=True)

# Ensure essential directories exist
for d in [
    DATA_DIR, RAW_DIR, PROCESSED_DIR, CHUNK_DIR, 
    EMBEDDING_DIR, VECTOR_DB_DIR, KG_DIR, INVENTORY_DIR, LOG_DIR
]:
    d.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".csv",
    ".txt",
}