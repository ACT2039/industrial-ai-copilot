"""
Analytics Panel Component
"""
import streamlit as st

def render_analytics_panel():
    """
    Renders professional KPI cards dynamically populated from backend states.
    """
    # Fetch live stats from session state
    results = st.session_state.get("retrieval_results", [])
    search_time = st.session_state.get("search_time", 0.0)
    subgraph = st.session_state.get("retrieved_subgraph", None)
    llm_time = st.session_state.get("llm_time", 0.0)
    total_time = st.session_state.get("total_time", 0.0)
    
    # Calculate retrieval KPIs
    retrieved_chunks = len(results)
    top_similarity = int(results[0].get("Score", 0) * 100) if results else 0
    avg_confidence = int(sum(r.get("Score", 0) for r in results) / retrieved_chunks * 100) if retrieved_chunks > 0 else 0
    
    # Calculate Graph KPIs
    if subgraph is not None:
        nodes_retrieved = subgraph.number_of_nodes()
        edges_traversed = subgraph.number_of_edges()
    else:
        nodes_retrieved = 0
        edges_traversed = 0
        
    subgraph_size = f"{nodes_retrieved + edges_traversed:,}"
    
    # Calculate static DB KPIs
    meta_df = st.session_state.get("metadata_df")
    indexed_docs = len(meta_df["File_Name"].unique()) if meta_df is not None and "File_Name" in meta_df.columns else 0
    embeddings_count = len(meta_df) if meta_df is not None else 0
    
    # Format numbers
    embeddings_str = f"{embeddings_count/1000000:.1f}M" if embeddings_count > 1000000 else f"{embeddings_count:,}"
    
    st.markdown(
        f"""
        <div class="glass-card" style="height: 100%; overflow-y: auto;">
            <div style="margin-bottom: 20px;">
                <h3 style="margin: 0; color: #f8fafc; font-size: 1.2rem; font-weight: 600;">System Analytics</h3>
                <p style="color: #94a3b8; font-size: 0.85rem; margin: 5px 0 0 0;">Real-time Pipeline & GraphRAG metrics.</p>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <!-- Pipeline KPI 1 -->
                <div style="background: rgba(15,23,42,0.6); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="color: #94a3b8; font-size: 0.7rem; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">E2E Pipeline Time</div>
                    <div style="color: #38bdf8; font-size: 1.5rem; font-weight: 700; margin-top: 5px;">{total_time}s</div>
                </div>
                
                <!-- Pipeline KPI 2 -->
                <div style="background: rgba(15,23,42,0.6); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="color: #94a3b8; font-size: 0.7rem; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">LLM Generation</div>
                    <div style="color: #38bdf8; font-size: 1.5rem; font-weight: 700; margin-top: 5px;">{llm_time}s</div>
                </div>
                
                <!-- Retrieval KPI 1 -->
                <div style="background: rgba(15,23,42,0.6); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="color: #94a3b8; font-size: 0.7rem; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">Retrieved Chunks</div>
                    <div style="color: #f8fafc; font-size: 1.5rem; font-weight: 700; margin-top: 5px;">{retrieved_chunks}</div>
                </div>
                
                <!-- Retrieval KPI 2 -->
                <div style="background: rgba(15,23,42,0.6); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="color: #94a3b8; font-size: 0.7rem; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">Search Time</div>
                    <div style="color: #f8fafc; font-size: 1.5rem; font-weight: 700; margin-top: 5px;">{search_time}s</div>
                </div>
                
                <!-- Graph KPI 1 -->
                <div style="background: rgba(15,23,42,0.6); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="color: #94a3b8; font-size: 0.7rem; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">Graph Nodes</div>
                    <div style="color: #10b981; font-size: 1.5rem; font-weight: 700; margin-top: 5px;">{nodes_retrieved:,}</div>
                </div>
                
                <!-- Graph KPI 2 -->
                <div style="background: rgba(15,23,42,0.6); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="color: #94a3b8; font-size: 0.7rem; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">Traversed Edges</div>
                    <div style="color: #10b981; font-size: 1.5rem; font-weight: 700; margin-top: 5px;">{edges_traversed:,}</div>
                </div>
                
                <!-- Static KPI 1 -->
                <div style="background: rgba(15,23,42,0.6); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="color: #94a3b8; font-size: 0.7rem; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">Indexed Docs</div>
                    <div style="color: #cbd5e1; font-size: 1.5rem; font-weight: 700; margin-top: 5px;">{indexed_docs:,}</div>
                </div>
                
                <!-- Static KPI 2 -->
                <div style="background: rgba(15,23,42,0.6); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="color: #94a3b8; font-size: 0.7rem; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">Total Embeddings</div>
                    <div style="color: #cbd5e1; font-size: 1.5rem; font-weight: 700; margin-top: 5px;">{embeddings_str}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
