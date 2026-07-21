"""
Sidebar Component
"""
import streamlit as st

def render_sidebar():
    """
    Renders the elegant navigation sidebar and System Status card.
    """
    with st.sidebar:
        st.markdown(
            """
            <div style="margin-bottom: 40px;">
                <h2 style="color: #f8fafc; font-weight: 700; font-size: 1.8rem; letter-spacing: 1px;">
                    NEXUS<span style="color: #38bdf8;">.</span>
                </h2>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.button("🏠 Dashboard", use_container_width=True)
        st.button("📄 Documents", use_container_width=True)
        st.button("📊 Analytics", use_container_width=True)
        st.button("⚙️ Settings", use_container_width=True)
        st.button("ℹ️ About", use_container_width=True)
        
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # System Status Card
        status_card = """
        <div class="glass-card" style="padding: 15px;">
            <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px;">
                System Status
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px; font-size: 0.85rem; color: #cbd5e1;">
                <div style="display: flex; align-items: center;"><span class="dot-green"></span> OpenRouter</div>
                <div style="display: flex; align-items: center;"><span class="dot-green"></span> FAISS</div>
                <div style="display: flex; align-items: center;"><span class="dot-green"></span> Knowledge Graph</div>
                <div style="display: flex; align-items: center;"><span class="dot-green"></span> Embedding Model</div>
                <div style="display: flex; align-items: center;"><span class="dot-green"></span> Enterprise Mode</div>
            </div>
        </div>
        """
        st.markdown(status_card, unsafe_allow_html=True)
