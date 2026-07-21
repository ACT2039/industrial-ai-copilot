"""
Header Component
"""
import streamlit as st

def render_header():
    """
    Renders the premium header with dot-separated subtitles and online status.
    """
    header_html = """
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-top: -30px; margin-bottom: 30px;">
        <div>
            <h1 style="margin: 0; padding: 0; font-size: 2.8rem; font-weight: 700; display: flex; align-items: center; gap: 10px;">
                🧠 <span style="background: linear-gradient(135deg, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">NEXUS AI</span>
            </h1>
            <p style="margin: 5px 0 15px 0; color: #94a3b8; font-size: 1.1rem; letter-spacing: 1px;">Enterprise Knowledge Intelligence Platform</p>
            <div style="display: flex; gap: 15px; color: #64748b; font-size: 0.9rem; font-weight: 500;">
                <span style="color: #38bdf8;">GraphRAG</span> •
                <span>Semantic Search</span> •
                <span>Knowledge Graph</span> •
                <span>Enterprise AI</span>
            </div>
        </div>
        <div style="display: flex; align-items: center; background: rgba(16, 185, 129, 0.1); padding: 8px 16px; border-radius: 20px; border: 1px solid rgba(16, 185, 129, 0.3);">
            <span class="dot-green animate-pulse"></span>
            <span style="color: #10b981; font-weight: 500; font-size: 0.9rem; letter-spacing: 0.5px;">System Online</span>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
