"""
Enterprise Knowledge Intelligence Platform - Main Application Entry Point
"""
import streamlit as st
import os
import time

# Must be the first Streamlit command
# Deployment Marker
APP_VERSION = "Build 2026-07-22 18:30"

st.set_page_config(
    page_title="NEXUS AI Enterprise Copilot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Late imports to ensure st.set_page_config runs first
from pages import home
from components import sidebar
from components import header
from services.config_service import load_config
from services.retrieval_service import load_faiss_index, load_metadata_and_chunks
from services.graph_service import load_knowledge_graph

def load_css():
    """Loads custom CSS for premium styling."""
    css_path = os.path.join(os.path.dirname(__file__), "styles", "main.css")
    try:
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def render_splash_screen():
    """Renders the animated startup sequence and performs backend validation."""
    if 'initialized' not in st.session_state:
        placeholder = st.empty()
        
        html_content = """
        <div class="splash-container">
            <div class="splash-title">🧠 NEXUS AI</div>
            <div class="splash-subtitle">Enterprise Knowledge Intelligence Platform</div>
            <hr style="width: 300px; border-color: rgba(255,255,255,0.1); margin-bottom: 20px;">
            <div id="logs" style="text-align: left; width: 400px; height: 250px;">
        """
        
        def update_splash(msg, is_error=False, is_final=False):
            nonlocal html_content
            color = "#ef4444" if is_error else ("#38bdf8" if is_final else "#10b981")
            weight = "bold" if is_final else "normal"
            html_content += f'<div class="splash-log" style="color: {color}; font-weight: {weight}; margin-top: {"15px" if is_final else "5px"};">{msg}</div>'
            placeholder.markdown(html_content + "</div></div>", unsafe_allow_html=True)
            time.sleep(0.4) # Add slight delay for animation effect
            
        update_splash("Initializing Enterprise Intelligence...")
        
        # 1. Configuration
        config = load_config()
        if config.get("API_STATUS") == "Configured":
            update_splash("✓ Configuration Loaded")
        else:
            update_splash(f"⚠ Configuration Warning: {config.get('API_STATUS')}", is_error=True)
            
        # 2. FAISS Index
        index = load_faiss_index()
        if index is not None:
            update_splash("✓ FAISS Loaded")
        else:
            update_splash("✗ FAISS Index Failed to Load", is_error=True)
            
        # 3. Metadata & Chunks
        meta_df, chunks_df = load_metadata_and_chunks()
        if meta_df is not None and chunks_df is not None:
            update_splash("✓ Metadata Loaded")
        else:
            update_splash("✗ Metadata/Chunks Failed to Load", is_error=True)
            
        # 4. Knowledge Graph
        kg = load_knowledge_graph()
        if kg is not None:
            update_splash("✓ Knowledge Graph Loaded")
        else:
            update_splash("✗ Knowledge Graph Failed to Load", is_error=True)
            
        # Check overall status
        if index is not None and meta_df is not None and kg is not None:
            update_splash("✓ Resources Ready")
            time.sleep(0.5)
            update_splash("Launching Dashboard...", is_final=True)
            time.sleep(0.8)
        else:
            update_splash("⚠ Launching Dashboard with degraded functionality...", is_error=True)
            time.sleep(2)
        
        placeholder.empty()
        st.session_state['initialized'] = True
        
        # Store resources in session state for easy access globally
        st.session_state['config'] = config
        st.session_state['faiss_index'] = index
        st.session_state['metadata_df'] = meta_df
        st.session_state['chunks_df'] = chunks_df
        st.session_state['knowledge_graph'] = kg

def main():
    """
    Main execution function orchestrating the NEXUS AI dashboard.
    """
    load_css()
    
    # Run startup splash sequence and backend loaders
    render_splash_screen()
    
    # Render UI
    sidebar.render_sidebar()
    
    # Display deployment marker at the bottom of the sidebar
    st.sidebar.markdown(f"<div style='text-align: center; color: #888; font-size: 0.8rem; margin-top: 20px;'>{APP_VERSION}</div>", unsafe_allow_html=True)
    
    header.render_header()
    home.render_home()

if __name__ == "__main__":
    main()
