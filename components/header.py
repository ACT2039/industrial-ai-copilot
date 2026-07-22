"""
Header Component
"""
import streamlit as st

def clear_session():
    """Resets core session state variables and triggers a rerun."""
    keys_to_clear = [
        "retrieval_results", "search_time", "llm_answer", "llm_time", 
        "total_time", "tokens_used", "last_query", "retrieved_subgraph"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
            
    st.session_state["is_processing"] = False

def render_header():
    """
    Renders the unified enterprise top header natively.
    """
    st.markdown("<div id='nexus-header'><h1 style='margin-bottom: 0; padding-bottom: 0;'>NEXUS AI Workspace</h1></div>", unsafe_allow_html=True)
    st.write("") # Minimal spacing before Copilot
