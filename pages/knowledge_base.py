"""
Knowledge Base Dashboard

Provides UI for uploading, managing, and monitoring the Enterprise Knowledge Base.
"""
import streamlit as st
import pandas as pd
import faiss
import time
from pathlib import Path
from services.config_service import ResourceLoader
from services.ingestion_service import ingest_documents, delete_document
from components.theme import inject_theme

def render_knowledge_base():
    """Renders the Knowledge Base management dashboard."""
    inject_theme()
    
    st.title("📚 Knowledge Base Management")
    st.caption("Upload, monitor, and manage the industrial documents powering NEXUS AI.")
    
    # Check dependencies
    try:
        import fitz
    except ImportError:
        st.error("PyMuPDF (fitz) is required for PDF parsing. Please install it via `pip install PyMuPDF`.")
        st.stop()
        
    meta_path = ResourceLoader.get_faiss_metadata_path()
    chunks_path = ResourceLoader.get_chunks_path()
    kg_path = ResourceLoader.get_knowledge_graph_path()
    
    try:
        meta_df = pd.read_parquet(meta_path)
        chunks_df = pd.read_parquet(chunks_path)
        import pickle
        with open(kg_path, 'rb') as f:
            kg = pickle.load(f)
    except Exception as e:
        st.error(f"Failed to load backend resources: {e}")
        return
        
    # Remove DELETED documents from stats and view
    active_mask = meta_df['File_Name'] != 'DELETED'
    active_meta = meta_df[active_mask]
    
    # ---------------------------------------------------------
    # PART 1: KPI Dashboard
    # ---------------------------------------------------------
    total_docs = active_meta['File_Name'].nunique()
    total_chunks = len(active_meta)
    total_nodes = kg.number_of_nodes()
    total_edges = kg.number_of_edges()
    db_size_mb = round(meta_path.stat().st_size / (1024 * 1024), 2)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Indexed Documents", total_docs)
    col2.metric("Knowledge Chunks", total_chunks)
    col3.metric("Graph Entities", total_nodes)
    col4.metric("Vector DB Size (MB)", db_size_mb)
    
    st.divider()
    
    # ---------------------------------------------------------
    # PART 2 & 3: Document Upload Pipeline
    # ---------------------------------------------------------
    st.subheader("Cloud Ingestion Pipeline")
    uploaded_files = st.file_uploader(
        "Upload new manuals, SOPs, or industrial logs", 
        type=["pdf", "txt", "md"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("Start Ingestion Pipeline", type="primary"):
            with st.status("Initializing Upload...", expanded=True) as status:
                success = ingest_documents(uploaded_files, status)
                if success:
                    st.success("Ingestion complete. The AI Copilot is now aware of the new documents.")
                    time.sleep(1)
                    st.rerun()
                    
    st.divider()
    
    # ---------------------------------------------------------
    # PART 4 & 5: Document Management
    # ---------------------------------------------------------
    st.subheader("Indexed Documents")
    
    if active_meta.empty:
        st.info("No active documents in the Knowledge Base.")
    else:
        # Aggregate document stats
        doc_stats = active_meta.groupby('File_Name').agg(
            Chunks=('Chunk_ID', 'count'),
            Source=('Source', 'first')
        ).reset_index()
        
        doc_stats['Actions'] = "Select a document below to manage"
        
        st.dataframe(
            doc_stats,
            use_container_width=True,
            hide_index=True,
            column_config={
                "File_Name": st.column_config.TextColumn("Document Name"),
                "Chunks": st.column_config.NumberColumn("Indexed Chunks"),
                "Source": st.column_config.TextColumn("Upload Source"),
            }
        )
        
        # Document Selection for Actions
        st.markdown("### Manage Document")
        selected_doc = st.selectbox("Select a document to modify:", ["None"] + doc_stats['File_Name'].tolist())
        
        if selected_doc != "None":
            st.info(f"Selected: **{selected_doc}**")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔍 View Details", use_container_width=True):
                    st.write(f"This document generated **{doc_stats[doc_stats['File_Name'] == selected_doc]['Chunks'].values[0]}** semantic chunks.")
            with col_b:
                if st.button("🗑️ Delete Document", type="primary", use_container_width=True):
                    with st.spinner("Safely removing from FAISS and Graph..."):
                        success, msg = delete_document(selected_doc)
                        if success:
                            st.success(msg)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)

if __name__ == "__main__":
    render_knowledge_base()
