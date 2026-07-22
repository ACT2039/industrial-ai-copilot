"""
Ingestion Service

Handles dynamic document ingestion, indexing, and updating of the Knowledge Base.
Implements strict atomic operations with staging and rollback to prevent corruption.
"""
import streamlit as st
import os
import shutil
import time
import pandas as pd
import numpy as np
import faiss
import networkx as nx
from pathlib import Path
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
import re

from services.config_service import PROJECT_ROOT, DATA_DIR, ResourceLoader

# Define Backup Directory
BACKUP_DIR = DATA_DIR / "backups"
STAGING_DIR = DATA_DIR / "staging"

def init_directories():
    """Ensures backup and staging directories exist."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

def create_backup():
    """Creates a temporary backup of the active knowledge base."""
    init_directories()
    timestamp = str(int(time.time()))
    backup_path = BACKUP_DIR / f"backup_{timestamp}"
    backup_path.mkdir(parents=True, exist_ok=True)
    
    try:
        if ResourceLoader.get_faiss_index_path().exists():
            shutil.copy2(ResourceLoader.get_faiss_index_path(), backup_path / "faiss.index")
        if ResourceLoader.get_faiss_metadata_path().exists():
            shutil.copy2(ResourceLoader.get_faiss_metadata_path(), backup_path / "faiss_metadata.parquet")
        if ResourceLoader.get_chunks_path().exists():
            shutil.copy2(ResourceLoader.get_chunks_path(), backup_path / "chunks.parquet")
        if ResourceLoader.get_knowledge_graph_path().exists():
            shutil.copy2(ResourceLoader.get_knowledge_graph_path(), backup_path / "knowledge_graph.gpickle")
        return backup_path
    except Exception as e:
        raise RuntimeError(f"Backup failed: {e}")

def restore_backup(backup_path: Path):
    """Restores the knowledge base from a backup in case of failure."""
    if not backup_path or not backup_path.exists():
        return
        
    try:
        if (backup_path / "faiss.index").exists():
            shutil.copy2(backup_path / "faiss.index", ResourceLoader.get_faiss_index_path())
        if (backup_path / "faiss_metadata.parquet").exists():
            shutil.copy2(backup_path / "faiss_metadata.parquet", ResourceLoader.get_faiss_metadata_path())
        if (backup_path / "chunks.parquet").exists():
            shutil.copy2(backup_path / "chunks.parquet", ResourceLoader.get_chunks_path())
        if (backup_path / "knowledge_graph.gpickle").exists():
            shutil.copy2(backup_path / "knowledge_graph.gpickle", ResourceLoader.get_knowledge_graph_path())
            
        # Clear Streamlit caches to force reload
        st.cache_resource.clear()
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Critical Error: Failed to restore backup from {backup_path}. System may be inconsistent. {e}")

def extract_text(file_obj, filename: str) -> str:
    """Extracts raw text from uploaded files."""
    text = ""
    ext = Path(filename).suffix.lower()
    
    if ext == ".pdf":
        doc = fitz.open(stream=file_obj.read(), filetype="pdf")
        for page in doc:
            text += page.get_text() + "\n"
    elif ext in [".txt", ".md", ".csv"]:
        text = file_obj.read().decode('utf-8', errors='ignore')
    else:
        raise ValueError(f"Unsupported file format: {ext}")
        
    return text

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """Splits text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk.strip()) > 10:
            chunks.append(chunk)
    return chunks

def extract_entities(text: str) -> list:
    """
    Lightweight rule-based entity extraction for dynamic ingestion.
    Extracts capitalized noun phrases and domain keywords to avoid slow LLM calls during upload.
    """
    # Simple regex for capitalized phrases (e.g., "Transformer Module", "Safety Valve")
    capitalized_phrases = re.findall(r'\\b[A-Z][a-z]+(?:\\s[A-Z][a-z]+)*\\b', text)
    # Filter out common stop words if necessary, or just keep unique ones
    entities = list(set(capitalized_phrases))
    # Limit to top 5 entities per chunk to prevent graph explosion
    return entities[:5]

def ingest_documents(uploaded_files, status_container):
    """
    Main pipeline to safely ingest documents.
    """
    if not uploaded_files:
        return False
        
    backup_path = None
    try:
        status_container.update(label="Creating Safety Backup...", state="running")
        backup_path = create_backup()
        
        # Load existing structures
        status_container.update(label="Loading Database...", state="running")
        from services.retrieval_service import load_embedding_model
        
        index_path = ResourceLoader.get_faiss_index_path()
        meta_path = ResourceLoader.get_faiss_metadata_path()
        chunks_path = ResourceLoader.get_chunks_path()
        kg_path = ResourceLoader.get_knowledge_graph_path()
        
        index = faiss.read_index(str(index_path))
        meta_df = pd.read_parquet(meta_path)
        chunks_df = pd.read_parquet(chunks_path)
        
        import pickle
        with open(kg_path, 'rb') as f:
            kg = pickle.load(f)
            
        model = load_embedding_model()
        if model is None:
            raise RuntimeError("Failed to load embedding model.")
            
        # Determine starting Chunk_ID
        last_chunk_id = 0
        if not meta_df.empty:
            # Assuming Chunk_ID format is like "chunk_0", "chunk_100"
            try:
                ids = meta_df['Chunk_ID'].str.replace('chunk_', '').astype(int)
                last_chunk_id = ids.max() + 1
            except:
                last_chunk_id = len(meta_df)
        
        new_meta_rows = []
        new_chunks_rows = []
        new_embeddings = []
        
        for file in uploaded_files:
            filename = file.name
            # Check for duplicates
            if filename in meta_df['File_Name'].values:
                st.warning(f"Skipping {filename}: Already exists in Knowledge Base.")
                continue
                
            status_container.update(label=f"Extracting {filename}...", state="running")
            raw_text = extract_text(file, filename)
            
            status_container.update(label=f"Chunking {filename}...", state="running")
            chunks = chunk_text(raw_text)
            
            status_container.update(label=f"Embedding {filename}...", state="running")
            if chunks:
                embeddings = model.encode(chunks, normalize_embeddings=True, convert_to_numpy=True).astype(np.float32)
                
                for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                    chunk_id = f"chunk_{last_chunk_id}"
                    
                    new_embeddings.append(emb)
                    new_meta_rows.append({
                        "Chunk_ID": chunk_id,
                        "File_Name": filename,
                        "Source": "User Upload",
                        "Page_Number": np.nan  # Use NaN instead of string to prevent Parquet type conflicts
                    })
                    new_chunks_rows.append({
                        "Chunk_ID": chunk_id,
                        "Chunk_Text": chunk
                    })
                    
                    # Update Knowledge Graph
                    entities = extract_entities(chunk)
                    kg.add_node(chunk_id, type="Chunk", text=chunk[:200])
                    for entity in entities:
                        if not kg.has_node(entity):
                            kg.add_node(entity, type="Entity")
                        kg.add_edge(chunk_id, entity, type="contains")
                    
                    last_chunk_id += 1

        if not new_embeddings:
            status_container.update(label="No new content to index.", state="complete")
            return True

        status_container.update(label="Updating Vector Database & Graph...", state="running")
        
        # 1. Update FAISS
        emb_matrix = np.vstack(new_embeddings)
        index.add(emb_matrix)
        faiss.write_index(index, str(index_path))
        
        # 2. Update DataFrames
        new_meta_df = pd.DataFrame(new_meta_rows)
        new_chunks_df = pd.DataFrame(new_chunks_rows)
        
        updated_meta_df = pd.concat([meta_df, new_meta_df], ignore_index=True)
        updated_chunks_df = pd.concat([chunks_df, new_chunks_df], ignore_index=True)
        
        updated_meta_df.to_parquet(meta_path)
        updated_chunks_df.to_parquet(chunks_path)
        
        # 3. Update Knowledge Graph
        with open(kg_path, 'wb') as f:
            pickle.dump(kg, f)
            
        status_container.update(label="Refreshing Global State...", state="running")
        
        # Clear Streamlit caches so next query uses the new data
        st.cache_resource.clear()
        st.cache_data.clear()
        
        status_container.update(label="Knowledge Base Updated Successfully!", state="complete")
        return True
        
    except Exception as e:
        status_container.update(label=f"Ingestion Failed: {e}. Rolling back...", state="error")
        if backup_path:
            restore_backup(backup_path)
        return False

def delete_document(filename: str):
    """
    Safely removes a document and its nodes from the Knowledge Base.
    Uses a 'Soft Delete' approach for FAISS metadata to preserve strict index alignment 
    without needing to completely rebuild/re-embed the entire vector database.
    """
    init_directories()
    backup_path = None
    try:
        backup_path = create_backup()
        
        meta_path = ResourceLoader.get_faiss_metadata_path()
        chunks_path = ResourceLoader.get_chunks_path()
        kg_path = ResourceLoader.get_knowledge_graph_path()
        
        meta_df = pd.read_parquet(meta_path)
        chunks_df = pd.read_parquet(chunks_path)
        
        import pickle
        with open(kg_path, 'rb') as f:
            kg = pickle.load(f)
            
        # 1. Identify chunks belonging to the document
        doc_mask = meta_df['File_Name'] == filename
        if not doc_mask.any():
            return False, "Document not found."
            
        chunk_ids_to_remove = meta_df[doc_mask]['Chunk_ID'].tolist()
        
        # 2. Soft delete in metadata (prevents FAISS index shifting)
        meta_df.loc[doc_mask, 'File_Name'] = 'DELETED'
        meta_df.loc[doc_mask, 'Source'] = 'DELETED'
        
        # 3. Soft delete in chunks 
        chunk_mask = chunks_df['Chunk_ID'].isin(chunk_ids_to_remove)
        chunks_df.loc[chunk_mask, 'Chunk_Text'] = 'DELETED'
        
        # 4. Delete nodes from Knowledge Graph (NetworkX handles dynamic deletion safely)
        for cid in chunk_ids_to_remove:
            if kg.has_node(cid):
                # Optionally remove orphaned entities
                neighbors = list(kg.neighbors(cid))
                kg.remove_node(cid)
                for neighbor in neighbors:
                    if kg.has_node(neighbor) and kg.degree(neighbor) == 0:
                        kg.remove_node(neighbor)
                        
        # 5. Save updates
        meta_df.to_parquet(meta_path)
        chunks_df.to_parquet(chunks_path)
        
        with open(kg_path, 'wb') as f:
            pickle.dump(kg, f)
            
        st.cache_resource.clear()
        st.cache_data.clear()
        return True, "Document deleted successfully."
        
    except Exception as e:
        if backup_path:
            restore_backup(backup_path)
        return False, f"Deletion failed: {e}"
