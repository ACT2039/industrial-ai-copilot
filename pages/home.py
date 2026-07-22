"""
Home Page
"""
import streamlit as st
from components import chat_panel, graph_panel, evidence_panel, analytics_panel, explainability_panel, explorer_panel, theme

def render_home():
    """
    Renders the unified, single-column premium dashboard.
    Fixes execution order bugs and applies the global glassmorphism theme.
    """
    # 1. Apply Global UX Theme
    theme.inject_theme()
    
    # 2. Main Copilot Focus (Top Center)
    chat_panel.render_chat_panel()
    
    st.write("")
    st.write("")
    
    # 3. Knowledge Explorer & Graph (Preview Mode)
    with st.container():
        st.subheader("Enterprise Graph Analytics", anchor=False)
        st.caption("Visual explanation of how the AI navigated your enterprise data to construct its answer.")
        
        exp_col, graph_col = st.columns([1, 3], gap="large")
        with exp_col:
            explorer_panel.render_explorer_panel()
        with graph_col:
            graph_panel.render_graph_panel(full_screen=False)
            
    st.write("---")
    
    # 4. Explainability
    explainability_panel.render_explainability_panel()
    
    st.write("---")
    
    # 5. Evidence
    evidence_panel.render_evidence_panel()
    
    st.write("---")
    
    # 6. Analytics
    analytics_panel.render_analytics_panel()
