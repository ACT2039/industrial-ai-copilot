"""
Analytics Panel Component
"""
import streamlit as st

def render_analytics_panel():
    """
    Renders professional 10-point KPI array dynamically populated from backend states.
    """
    # Fetch live stats from session state
    results = st.session_state.get("retrieval_results", [])
    search_time = st.session_state.get("search_time", 0.0)
    graph_time = st.session_state.get("graph_time", 0.0)
    subgraph = st.session_state.get("retrieved_subgraph", None)
    llm_time = st.session_state.get("llm_time", 0.0)
    total_time = st.session_state.get("total_time", 0.0)
    tokens_used = st.session_state.get("tokens_used", 0)
    overall_conf = st.session_state.get("overall_confidence", 0.0)
    
    retrieved_chunks = len(results)
    docs_referenced = len(set([res.get("Document_Name", "Unknown") for res in results]))
    
    if subgraph is not None:
        nodes_retrieved = subgraph.number_of_nodes()
        edges_traversed = subgraph.number_of_edges()
    else:
        nodes_retrieved = 0
        edges_traversed = 0
        
    st.subheader("System Metrics", anchor=False)
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Pipeline Time", value=f"{total_time}s")
            st.metric(label="Graph Expansion Time", value=f"{graph_time}s")
            st.metric(label="Tokens Used", value=f"{tokens_used:,}")
            st.metric(label="Retrieved Chunks", value=f"{retrieved_chunks}")
            st.metric(label="Relationships Traversed", value=f"{edges_traversed:,}")
        with col2:
            st.metric(label="Retrieval Time", value=f"{search_time}s")
            st.metric(label="LLM Time", value=f"{llm_time}s")
            st.metric(label="Overall Confidence", value=f"{int(overall_conf * 100)}%")
            st.metric(label="Retrieved Documents", value=f"{docs_referenced}")
            st.metric(label="Graph Nodes", value=f"{nodes_retrieved:,}")
