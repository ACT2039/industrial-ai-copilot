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
    
    # Use Streamlit's recommended Tabs pattern for layout
    # This prevents vertical stacking and keeps the chat focused
    chat_tab, graph_tab, explain_tab, evidence_tab, analytics_tab = st.tabs([
        "💬 Copilot", 
        "🕸️ Enterprise Graph", 
        "🧠 Explainability",
        "📄 Evidence", 
        "📈 Analytics"
    ])
    
    with chat_tab:
        chat_panel.render_chat_history()
        
    with graph_tab:
        st.subheader("Enterprise Graph Analytics", anchor=False)
        st.caption("Visual explanation of how the AI navigated your enterprise data to construct its answer.")
        exp_col, graph_col = st.columns([1, 3], gap="large")
        with exp_col:
            explorer_panel.render_explorer_panel()
        with graph_col:
            graph_panel.render_graph_panel(full_screen=False)
            
    with explain_tab:
        explainability_panel.render_explainability_panel()
        
    with evidence_tab:
        evidence_panel.render_evidence_panel()
        
    with analytics_tab:
        analytics_panel.render_analytics_panel()

    # Natively sticky chat input at the bottom of the main viewport (outside tabs)
    chat_panel.render_chat_input()
