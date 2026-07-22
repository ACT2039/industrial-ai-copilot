"""
Retrieval Service

Handles the safe loading of the FAISS index, embedding models, and executes
semantic retrieval against the validated dataframes.
"""
import streamlit as st
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from services.config_service import ResourceLoader

@st.cache_resource(show_spinner=False)
def load_faiss_index():
    """
    Loads the FAISS index into memory, cached per session.
    """
    try:
        index_path = ResourceLoader.get_faiss_index_path()
        index = faiss.read_index(str(index_path))
        return index
    except Exception as e:
        st.error(f"Failed to load FAISS Index: {str(e)}")
        return None

@st.cache_data(show_spinner=False)
def load_metadata_and_chunks():
    """
    Loads the Parquet chunks and metadata into Pandas DataFrames, cached per session.
    Returns a tuple: (faiss_metadata_df, chunks_df)
    """
    try:
        metadata_path = ResourceLoader.get_faiss_metadata_path()
        chunks_path = ResourceLoader.get_chunks_path()
        
        metadata_df = pd.read_parquet(metadata_path)
        chunks_df = pd.read_parquet(chunks_path)
        
        return metadata_df, chunks_df
    except Exception as e:
        st.error(f"Failed to load DataFrames: {str(e)}")
        return None, None

@st.cache_resource(show_spinner=False)
def load_embedding_model(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    """
    Loads the sentence transformer embedding model, cached per session.
    """
    try:
        model = SentenceTransformer(model_name)
        return model
    except Exception as e:
        st.error(f"Failed to load Embedding Model: {str(e)}")
        return None

def search(query: str, top_k: int = 5) -> list:
    """
    Executes a semantic search against the FAISS index.
    Returns a list of structured dictionaries containing retrieval metadata and chunk text.
    """
    if not query.strip():
        return []

    # Fetch cached resources from Streamlit (loads them if not already in memory)
    index = load_faiss_index()
    meta_df, chunks_df = load_metadata_and_chunks()
    model = load_embedding_model()

    # Graceful degradation
    if index is None or meta_df is None or chunks_df is None or model is None:
        st.warning("Retrieval unavailable due to missing backend resources.")
        return []

    try:
        # Generate query embedding
        query_embedding = model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype(np.float32)

        # Search FAISS index
        scores, indices = index.search(query_embedding, top_k)

        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
            if idx == -1: # FAISS returns -1 for empty/invalid slots
                continue
                
            # Safely get metadata row
            if idx >= len(meta_df):
                continue
                
            meta_row = meta_df.iloc[idx]
            
            # Check for Soft Deleted documents
            if meta_row.get("File_Name") == "DELETED":
                continue
                
            chunk_id = meta_row.get("Chunk_ID")
            
            # Find matching chunk text
            chunk_match = chunks_df[chunks_df["Chunk_ID"] == chunk_id]
            if chunk_match.empty:
                chunk_text = "Chunk text unavailable."
            else:
                chunk_text = chunk_match.iloc[0].get("Chunk_Text", "Chunk text unavailable.")

            results.append({
                "Rank": rank,
                "Score": round(float(score), 4),
                "Chunk_ID": chunk_id,
                "Document_Name": meta_row.get("File_Name", "Unknown Document"),
                "Source": meta_row.get("Source", "Unknown"),
                "Page_Number": meta_row.get("Page_Number", "N/A"),
                "Chunk_Text": chunk_text
            })

        import datetime
        try:
            with open("data/deployment_debug.log", "a", encoding="utf-8") as f:
                f.write(f"\\n--- [RETRIEVAL DIAGNOSTICS] {datetime.datetime.now()} ---\\n")
                f.write(f"Number of retrieved chunks: {len(results)}\\n")
                for r in results:
                    f.write(f"ID: {r['Chunk_ID']}, Doc: {r['Document_Name']}, Page: {r['Page_Number']}, Score: {r['Score']}, Len: {len(r['Chunk_Text'])}\\n")
        except Exception:
            pass

        return results
    except Exception as e:
        st.error(f"Search failed: {str(e)}")
        return []
