"""
Analytics Panel Component
"""
import streamlit as st

def render_analytics_panel():
    """
    Renders professional 10-point KPI array dynamically populated from backend states.
    """
    metrics = st.session_state.get("pipeline_metrics", {})
    
    pipeline_time = metrics.get("pipeline_time", 0.0)
    retrieval_time = metrics.get("retrieval_time", 0.0)
    graph_time = metrics.get("graph_time", 0.0)
    prompt_time = metrics.get("prompt_time", 0.0)
    llm_time = metrics.get("llm_time", 0.0)
    
    prompt_tokens = metrics.get("prompt_tokens", 0)
    comp_tokens = metrics.get("completion_tokens", 0)
    total_tokens = metrics.get("total_tokens", 0)
    
    retrieved_chunks = metrics.get("retrieved_chunks", 0)
    docs_referenced = metrics.get("retrieved_documents", 0)
    nodes_retrieved = metrics.get("graph_nodes", 0)
    edges_traversed = metrics.get("graph_edges", 0)
    
    context_length = metrics.get("context_length", 0)
    prompt_length = metrics.get("prompt_length", 0)
    overall_conf = metrics.get("confidence", "Unknown")
    model_name = metrics.get("model_name", "None")
    finish_reason = metrics.get("finish_reason", "None")
        
    st.subheader("System Metrics", anchor=False)
    
    with st.container(border=True):
        st.markdown("**⏱️ Latency & Execution**")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pipeline Time", f"{pipeline_time}s")
        c2.metric("Retrieval Time", f"{retrieval_time}s")
        c3.metric("Graph Time", f"{graph_time}s")
        c4.metric("LLM Response Time", f"{llm_time}s")
        
        st.markdown("**🧠 Token Usage & LLM**")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Prompt Tokens", f"{prompt_tokens:,}")
        c2.metric("Completion Tokens", f"{comp_tokens:,}")
        c3.metric("Total Tokens", f"{total_tokens:,}")
        c4.metric("Model", model_name.split("/")[-1])
        
        st.markdown("**📚 Context & Grounding**")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Retrieved Chunks", f"{retrieved_chunks}")
        c2.metric("Retrieved Documents", f"{docs_referenced}")
        c3.metric("Context Length (chars)", f"{context_length:,}")
        c4.metric("Confidence", overall_conf)
        
        st.markdown("**🕸️ Knowledge Graph**")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Graph Nodes", f"{nodes_retrieved:,}")
        c2.metric("Edges Traversed", f"{edges_traversed:,}")
        c3.metric("Prompt Length (chars)", f"{prompt_length:,}")
        c4.metric("Finish Reason", finish_reason)
