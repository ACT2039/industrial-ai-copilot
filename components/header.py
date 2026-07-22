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
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("<h1 style='margin-bottom: 0; padding-bottom: 0;'>NEXUS AI Workspace</h1>", unsafe_allow_html=True)
        
    with col2:
        st.button("Clear Session", use_container_width=True, on_click=clear_session)
        
    st.write("") # Minimal spacing before Copilot
