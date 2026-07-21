"""
Home Page
"""
import streamlit as st
from components import chat_panel, graph_panel, evidence_panel, analytics_panel, status_bar

def render_home():
    """
    Renders the unified 2x2 dashboard grid and the bottom status bar.
    """
    # Create the 2x2 Grid with responsive columns
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        with st.container():
            chat_panel.render_chat_panel()
            
        st.markdown("<br>", unsafe_allow_html=True)
            
        with st.container():
            evidence_panel.render_evidence_panel()
            
    with col_right:
        with st.container():
            graph_panel.render_graph_panel()
            
        st.markdown("<br>", unsafe_allow_html=True)
            
        with st.container():
            analytics_panel.render_analytics_panel()
            
    # Render Pipeline Status Bar spanning full width at the bottom
    status_bar.render_status_bar()
