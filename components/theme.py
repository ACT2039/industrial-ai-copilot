"""
Premium UX Theme Injector
"""
import streamlit as st
import streamlit.components.v1 as components

def inject_theme():
    """Injects aggressive CSS to force the Light Pale Beach & Mocha theme, overriding any browser Dark Mode settings."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        html, body, .stApp {
            font-family: 'Poppins', sans-serif !important;
        }
        
        .material-symbols-rounded, 
        .material-icons, 
        [data-testid="stIconMaterial"], 
        .streamlit-expanderHeader span {
            font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        }
        
        /* Force Base Application Background and Gradients */
        .stApp {
            background-color: #FDFBF7 !important; /* Force Pale Beach Sand */
            background-image: radial-gradient(circle at top right, rgba(235, 222, 206, 0.4) 0%, transparent 40%),
                              radial-gradient(circle at bottom left, rgba(216, 140, 81, 0.15) 0%, transparent 40%) !important;
        }
        
        @keyframes ambientGlow {
            0% { box-shadow: 0 20px 50px rgba(139, 90, 43, 0.25), 0 4px 15px rgba(139, 90, 43, 0.15), inset 0 1px 1px rgba(255,255,255,0.8); border-color: rgba(216, 140, 81, 0.4); }
            50% { box-shadow: 0 25px 60px rgba(139, 90, 43, 0.35), 0 4px 20px rgba(139, 90, 43, 0.2), inset 0 1px 1px rgba(255,255,255,1); border-color: rgba(216, 140, 81, 0.7); }
            100% { box-shadow: 0 20px 50px rgba(139, 90, 43, 0.25), 0 4px 15px rgba(139, 90, 43, 0.15), inset 0 1px 1px rgba(255,255,255,0.8); border-color: rgba(216, 140, 81, 0.4); }
        }
        
        /* Force Text Colors Globally (Overriding Dark Mode localStorage) */
        .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp span, .stApp label, .stApp li, .stApp div, .stMarkdown {
            /* We must not force color on icons specifically, but we force it generally */
            color: #3E3228 !important;
        }
        
        /* Override specifically for headers and metric labels to ensure they don't stay white */
        [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        [data-testid="stMetricLabel"] {
            color: #75553B !important;
        }
        
        /* Enterprise Copilot Container (Light Glassmorphism & Depth System) */
        .copilot-premium {
            background: rgba(255, 255, 255, 0.85) !important;
            backdrop-filter: blur(24px) !important;
            -webkit-backdrop-filter: blur(24px) !important;
            border: 1px solid rgba(216, 140, 81, 0.3) !important;
            border-radius: 20px !important;
            padding: 8px !important;
            
            /* Outer floating shadow + Inner depth highlight */
            box-shadow: 0 20px 50px rgba(139, 90, 43, 0.25), 0 4px 15px rgba(139, 90, 43, 0.15), inset 0 1px 1px rgba(255,255,255,0.8) !important; 
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
            
            /* Idle subtle breathing animation */
            animation: ambientGlow 8s infinite alternate ease-in-out;
        }
        
        .copilot-premium:hover {
            transform: translateY(-2px);
            box-shadow: 0 30px 70px rgba(139, 90, 43, 0.35), 0 10px 25px rgba(139, 90, 43, 0.2), inset 0 1px 1px rgba(255,255,255,1) !important; 
            border-color: #D88C51 !important;
            animation: none !important; /* Stop pulsing on hover */
        }
        
        /* Focus Glow when interacting with chat */
        .copilot-premium:focus-within {
            box-shadow: 0 0 0 2px rgba(216, 140, 81, 0.6), 0 20px 50px rgba(139, 90, 43, 0.25), inset 0 1px 1px rgba(255,255,255,1) !important;
            border-color: #D88C51 !important;
            animation: none !important;
        }
        
        /* Hide default elements (Do not hide header, it contains the sidebar button!) */
        #MainMenu, footer {
            visibility: hidden;
        }
        
        /* Interactive Buttons */
        .stButton > button {
            background: rgba(255, 255, 255, 0.9) !important;
            backdrop-filter: blur(8px) !important;
            border: 1px solid rgba(216, 140, 81, 0.4) !important;
            color: #3E3228 !important;
            border-radius: 14px !important;
            font-weight: 600 !important;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
            box-shadow: 0 4px 12px rgba(216, 140, 81, 0.08), inset 0 1px 1px rgba(255,255,255,1) !important;
        }
        .stButton > button:hover {
            background: #ffffff !important;
            color: #C0703B !important;
            border-color: #D88C51 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(216, 140, 81, 0.15), inset 0 1px 1px rgba(255,255,255,1) !important;
        }
        .stButton > button:active {
            transform: scale(0.97) !important;
            box-shadow: 0 2px 5px rgba(216, 140, 81, 0.1) !important;
        }
        
        /* Chat Inputs */
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid rgba(216, 140, 81, 0.3) !important;
            color: #3E3228 !important;
            border-radius: 14px !important;
            padding: 14px 20px !important;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
            font-size: 1rem !important;
            transition: all 0.2s ease !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: #D88C51 !important;
            box-shadow: 0 0 0 3px rgba(216, 140, 81, 0.15), inset 0 2px 4px rgba(0,0,0,0.02) !important;
            background: #ffffff !important;
        }
        
        /* PERFECT INPUT BAR ALIGNMENT (Task 1) */
        /* Targets the text input and send button specifically inside the chat container */
        .copilot-premium div[data-testid="stHorizontalBlock"] .stTextInput input {
            height: 52px !important;
            line-height: 52px !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
        .copilot-premium div[data-testid="stHorizontalBlock"] .stButton button {
            height: 52px !important;
            margin-top: 28px !important; /* Align with Streamlit's label offset */
        }
        
        /* Hide default 'Press Enter to apply' tooltip to prevent overlap on long text */
        div[data-testid="InputInstructions"] {
            display: none !important;
        }
        
        /* Status Bar / Expander */
        .st-emotion-cache-p5msec {
            background-color: transparent !important;
        }
        .streamlit-expanderHeader {
            background: rgba(255, 255, 255, 0.6) !important;
            border-radius: 8px !important;
            color: #3E3228 !important;
        }
        
        /* Metric values */
        div[data-testid="stMetricValue"] {
            font-weight: 800 !important;
            color: #C0703B !important;
        }
        
        /* Sidebar & History Items Styling */
        [data-testid="stSidebar"] {
            background: rgba(253, 251, 247, 0.85) !important;
            backdrop-filter: blur(24px) !important;
            -webkit-backdrop-filter: blur(24px) !important;
            border-right: 1px solid rgba(216, 140, 81, 0.3) !important;
            box-shadow: 5px 0 15px rgba(139, 90, 43, 0.05);
        }
        
        [data-testid="stSidebar"] button[key^="load_"] {
            text-align: left !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            color: #3E3228 !important;
            padding: 8px 12px !important;
            margin-bottom: 4px !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
        }
        
        [data-testid="stSidebar"] button[key^="load_"]:hover {
            background: rgba(216, 140, 81, 0.15) !important;
            transform: translateX(4px) !important;
            color: #C0703B !important;
        }
        </style>
    """, unsafe_allow_html=True)
