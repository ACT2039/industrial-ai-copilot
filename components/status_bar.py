"""
Status Bar Component
"""
import streamlit as st

def render_status_bar():
    """
    Renders a connected pipeline visualization at the bottom of the dashboard.
    """
    pipeline_html = """
    <div style="margin-top: 40px;">
        <h4 style="color: #94a3b8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px;">Live Data Pipeline</h4>
        
        <div class="pipeline-container">
            <div class="pipeline-line"></div>
            
            <div class="pipeline-stage">
                <div class="pipeline-node"></div>
                <span>Upload</span>
            </div>
            
            <div class="pipeline-stage">
                <div class="pipeline-node"></div>
                <span>Inventory</span>
            </div>
            
            <div class="pipeline-stage">
                <div class="pipeline-node"></div>
                <span>OCR</span>
            </div>
            
            <div class="pipeline-stage">
                <div class="pipeline-node"></div>
                <span>Chunking</span>
            </div>
            
            <div class="pipeline-stage">
                <div class="pipeline-node"></div>
                <span>Embeddings</span>
            </div>
            
            <div class="pipeline-stage">
                <div class="pipeline-node"></div>
                <span>FAISS</span>
            </div>
            
            <div class="pipeline-stage">
                <div class="pipeline-node"></div>
                <span>KG</span>
            </div>
            
            <div class="pipeline-stage">
                <div class="pipeline-node"></div>
                <span>Hybrid</span>
            </div>
            
            <div class="pipeline-stage">
                <div class="pipeline-node" style="box-shadow: 0 0 15px rgba(56, 189, 248, 0.8); border-color: #38bdf8; background: rgba(56,189,248,0.2);"></div>
                <span style="color: #38bdf8; font-weight: 600;">Response</span>
            </div>
        </div>
    </div>
    """
    st.markdown(pipeline_html, unsafe_allow_html=True)
