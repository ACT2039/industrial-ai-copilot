"""
Graph Panel Component
"""
import streamlit as st
import streamlit.components.v1 as components
from services.graph_service import get_subgraph
import networkx as nx

def render_placeholder():
    """Renders the animated SVG Knowledge Graph placeholder."""
    svg_graph = """
    <div class="glass-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; overflow: hidden; position: relative; padding: 40px 20px;">
        <svg viewBox="0 0 400 300" style="width: 100%; height: 200px; opacity: 0.8; margin-bottom: 20px;">
            <defs>
                <radialGradient id="glow" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.8"/>
                    <stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/>
                </radialGradient>
            </defs>
            
            <line x1="200" y1="150" x2="100" y2="80" stroke="rgba(56,189,248,0.3)" stroke-width="2" class="animate-pulse" />
            <line x1="200" y1="150" x2="320" y2="100" stroke="rgba(129,140,248,0.3)" stroke-width="2" />
            <line x1="200" y1="150" x2="150" y2="250" stroke="rgba(56,189,248,0.3)" stroke-width="1.5" />
            <line x1="200" y1="150" x2="280" y2="240" stroke="rgba(129,140,248,0.3)" stroke-width="1.5" class="animate-pulse" />
            <line x1="100" y1="80" x2="50" y2="120" stroke="rgba(255,255,255,0.1)" stroke-width="1" />
            <line x1="320" y1="100" x2="360" y2="160" stroke="rgba(255,255,255,0.1)" stroke-width="1" />
            
            <circle cx="200" cy="150" r="25" fill="url(#glow)" class="animate-pulse" />
            <circle cx="200" cy="150" r="10" fill="#f8fafc" />
            <circle cx="100" cy="80" r="15" fill="url(#glow)" />
            <circle cx="100" cy="80" r="6" fill="#38bdf8" />
            <circle cx="320" cy="100" r="18" fill="url(#glow)" class="animate-pulse" style="animation-delay: 1s;" />
            <circle cx="320" cy="100" r="8" fill="#818cf8" />
            <circle cx="150" cy="250" r="12" fill="url(#glow)" />
            <circle cx="150" cy="250" r="5" fill="#cbd5e1" />
            <circle cx="280" cy="240" r="14" fill="url(#glow)" />
            <circle cx="280" cy="240" r="6" fill="#38bdf8" />
        </svg>
        <h3 style="color: #f8fafc; font-size: 1.4rem; margin: 0 0 10px 0; font-weight: 600;">Knowledge Graph</h3>
        <p style="color: #94a3b8; font-size: 0.95rem; margin: 0; font-weight: 300;">Interactive graph will appear after retrieval.</p>
    </div>
    """
    st.markdown(svg_graph, unsafe_allow_html=True)

def render_graph_panel():
    """
    Renders an interactive PyVis Knowledge Graph if retrieval results exist,
    otherwise displays the animated SVG placeholder.
    """
    results = st.session_state.get("retrieval_results", [])
    
    if not results:
        render_placeholder()
        return
        
    with st.spinner("Generating Interactive Subgraph..."):
        subgraph = get_subgraph(results, depth=1)
        
        # Save subgraph to session state for Analytics Panel
        st.session_state["retrieved_subgraph"] = subgraph
        
        if subgraph.number_of_nodes() == 0:
            render_placeholder()
            st.warning("No linked entities found in Knowledge Graph for these chunks.")
            return

        try:
            from pyvis.network import Network
            
            # Configure PyVis Network
            net = Network(height="450px", width="100%", bgcolor="#0f172a", font_color="#e2e8f0")
            
            # Disable physics for large graphs to prevent lag, enable for small
            if subgraph.number_of_nodes() > 100:
                net.toggle_physics(False)
            
            # Transfer nodes and edges with styling
            for node, data in subgraph.nodes(data=True):
                node_type = data.get("type", "Unknown")
                color = "#38bdf8" if node_type == "Chunk" else ("#10b981" if node_type == "Document" else "#818cf8")
                size = 20 if node_type == "Chunk" else 15
                net.add_node(node, label=str(node)[:15], title=str(node), color=color, size=size)
                
            for source, target, data in subgraph.edges(data=True):
                rel = data.get("type", "")
                net.add_edge(source, target, title=rel, color="rgba(255,255,255,0.2)")

            # Generate HTML string
            html_string = net.generate_html()
            
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h3 style="margin: 0; color: #f8fafc; font-size: 1.2rem; font-weight: 600;">Entity Network</h3>
                    <span class="chip chip-green" style="font-size: 0.7rem;">{subgraph.number_of_nodes()} Nodes</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Render HTML inside a container matching the glass-card style
            st.markdown('<div class="glass-card" style="padding: 10px;">', unsafe_allow_html=True)
            components.html(html_string, height=460)
            st.markdown('</div>', unsafe_allow_html=True)
            
        except ImportError:
            st.error("PyVis is not installed. Run `pip install pyvis` to enable interactive graphs.")
            render_placeholder()
