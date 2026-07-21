"""
Configuration Service

Handles environment variable loading and validates the physical existence
of all required backend resources (FAISS, DataFrames, Knowledge Graph).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Define core paths based on project structure
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

class ResourceLoader:
    """
    Validates and locates physical pipeline outputs on disk.
    """
    
    @staticmethod
    def get_faiss_index_path() -> Path:
        path = DATA_DIR / "vector_db" / "faiss.index"
        if not path.exists():
            raise FileNotFoundError(f"FAISS index not found at {path}")
        return path

    @staticmethod
    def get_faiss_metadata_path() -> Path:
        path = DATA_DIR / "vector_db" / "faiss_metadata.parquet"
        if not path.exists():
            raise FileNotFoundError(f"FAISS metadata not found at {path}")
        return path

    @staticmethod
    def get_chunks_path() -> Path:
        path = DATA_DIR / "chunks" / "chunks.parquet"
        if not path.exists():
            raise FileNotFoundError(f"Chunks database not found at {path}")
        return path

    @staticmethod
    def get_knowledge_graph_path() -> Path:
        path = DATA_DIR / "knowledge_graph" / "knowledge_graph.gpickle"
        if not path.exists():
            raise FileNotFoundError(f"Knowledge Graph not found at {path}")
        return path

def load_config() -> dict:
    """
    Loads environment variables from .env and validates required settings.
    """
    env_path = PROJECT_ROOT / "config" / ".env"
    
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv() # Fallback to standard locations

    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    if not openrouter_key or openrouter_key == "dummy_key":
        # We don't crash, we just flag it so the UI can warn the user.
        api_status = "Missing or Invalid OpenRouter Key"
    else:
        api_status = "Configured"

    return {
        "OPENROUTER_API_KEY": openrouter_key,
        "API_STATUS": api_status
    }
