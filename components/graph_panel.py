"""
Graph Panel Component
"""
import streamlit as st
import streamlit.components.v1 as components
import networkx as nx
from services.retrieval_service import load_metadata_and_chunks
from services.graph_service import generate_semantic_label

def render_placeholder(height=800):
    """Renders a simple placeholder."""
    with st.container(border=True):
        for _ in range(int(height/60)):
            st.write("")
        st.info("Interactive Knowledge Graph will appear after retrieval.", icon="🕸️")
        for _ in range(int(height/60)):
            st.write("")

def inject_glass_ui(html_str, node_count, edge_count, density):
    """Injects premium Light Mode Glassmorphism UI into PyVis output."""
    
    custom_ui = f"""
    <style>
    /* Premium Light Glassmorphism Panel */
    .glass-panel {{
        position: absolute;
        top: 20px;
        left: 20px;
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(216, 140, 81, 0.4);
        border-radius: 16px;
        padding: 16px;
        color: #3E3228;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 8px 32px 0 rgba(117, 85, 59, 0.1);
        z-index: 9999;
        pointer-events: none;
    }}
    .glass-title {{
        font-size: 14px;
        font-weight: 800;
        margin-bottom: 10px;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        color: #75553B;
    }}
    .glass-stats {{
        font-size: 15px;
        color: #3E3228;
        font-weight: 500;
    }}
    .stat-row {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 6px;
        gap: 25px;
    }}
    .stat-val {{
        font-weight: 800;
        color: #C0703B; /* Terracotta Accent */
    }}
    
    /* Professional Legend Cards */
    .legend-container {{
        position: absolute;
        bottom: 20px;
        left: 20px;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        max-width: 65%;
        z-index: 9999;
    }}
    .legend-card {{
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(117, 85, 59, 0.2);
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        font-weight: 600;
        color: #3E3228;
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(117, 85, 59, 0.08);
    }}
    .legend-card:hover {{
        background: rgba(255, 255, 255, 1);
        border-color: rgba(216, 140, 81, 0.5);
        transform: translateY(-2px);
    }}
    .dot {{
        width: 14px;
        height: 14px;
        border-radius: 50%;
    }}
    
    /* Hide native vis.js navigation */
    .vis-navigation {{ display: none !important; }}
    
    /* Custom Premium Navigation Controls */
    .custom-nav {{
        position: absolute;
        bottom: 20px;
        right: 20px;
        display: flex;
        flex-direction: column;
        gap: 12px;
        z-index: 9999;
    }}
    .nav-btn {{
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(216, 140, 81, 0.4);
        color: #3E3228;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 20px;
        font-weight: bold;
        box-shadow: 0 6px 16px rgba(117, 85, 59, 0.15);
        transition: all 0.3s ease;
        user-select: none;
    }}
    .nav-btn:hover {{
        background: #D88C51;
        color: white;
        border-color: #C0703B;
        transform: scale(1.1);
        box-shadow: 0 8px 24px rgba(216, 140, 81, 0.35);
    }}
    </style>
    
    <div class="glass-panel">
        <div class="glass-title">Knowledge Insights</div>
        <div class="glass-stats">
            <div class="stat-row"><span>Displayed Entities:</span> <span class="stat-val">{node_count}</span></div>
            <div class="stat-row"><span>Relationships:</span> <span class="stat-val">{edge_count}</span></div>
            <div class="stat-row"><span>Graph Density:</span> <span class="stat-val">{density}%</span></div>
        </div>
    </div>
    
    <div class="legend-container">
        <div class="legend-card"><div class="dot" style="background:#3E6B7A;"></div> Equipment</div>
        <div class="legend-card"><div class="dot" style="background:#6B8E7B;"></div> Procedure</div>
        <div class="legend-card"><div class="dot" style="background:#A44A3F;"></div> Hazard</div>
        <div class="legend-card"><div class="dot" style="background:#D58936;"></div> Sensor</div>
        <div class="legend-card"><div class="dot" style="background:#755C6A;"></div> Document</div>
        <div class="legend-card"><div class="dot" style="background:#C0703B;"></div> Action</div>
    </div>
    
    <div class="custom-nav">
        <div class="nav-btn" onclick="network.fit({{animation: {{duration: 700, easingFunction: 'easeInOutCubic'}}}})" title="Fit Screen">⛶</div>
        <div class="nav-btn" onclick="var s=network.getScale(); network.moveTo({{scale: s*1.4, animation: {{duration: 400}}}})" title="Zoom In">+</div>
        <div class="nav-btn" onclick="var s=network.getScale(); network.moveTo({{scale: s/1.4, animation: {{duration: 400}}}})" title="Zoom Out">−</div>
    </div>
    """
    
    return html_str.replace("</body>", f"{custom_ui}\n</body>")


def render_graph_panel(full_screen=True):
    """
    Renders the AI Reasoning Graph with untangled physics, readable labels, and a premium Light Mode theme.
    """
    results = st.session_state.get("retrieval_results", [])
    
    # We now default to a massive 800px centralized container
    canvas_height = "800px" 
    
    if not results:
        render_placeholder(height=800)
        return
        
    subgraph = st.session_state.get("retrieved_subgraph")
    if not subgraph or subgraph.number_of_nodes() == 0:
        render_placeholder(height=800)
        st.warning("No linked entities found in Knowledge Graph for these chunks.")
        return

    # Streamlit Custom Controls (Placed above graph)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.caption("🔍 **Filter Entities**: Add or remove specific knowledge categories to declutter the visual graph.")
        selected_categories = st.multiselect(
            "Filter Categories", 
            ["Document", "Equipment", "Procedure", "Hazard", "Maintenance Action", "Sensor", "Context Entity"],
            default=["Document", "Equipment", "Procedure", "Hazard", "Maintenance Action", "Sensor", "Context Entity"],
            label_visibility="collapsed",
            placeholder="Filter by Category..."
        )
    with col2:
        st.caption("✨ **AI Logic Path**: Highlight the exact semantic pathway the AI traversed to answer your query.")
        show_path = st.toggle("Highlight AI Logic Path", value=True)

    with st.spinner("Untangling Topological Architecture..."):
        try:
            from pyvis.network import Network
            
            # Premium Light Mode Canvas
            net = Network(height=canvas_height, width="100%", bgcolor="#FDFBF7", font_color="#3E3228")
            
            active_chunk_ids = [res.get("Chunk_ID") for res in results]
            active_path_nodes = set(active_chunk_ids)
            for chunk_id in active_chunk_ids:
                if chunk_id in subgraph:
                    for neighbor in subgraph.neighbors(chunk_id):
                        active_path_nodes.add(neighbor)
                        
            meta_df, _ = load_metadata_and_chunks()
            
            edge_labels_map = ["requires", "contains", "connected_to", "prevents", "monitors", "depends_on", "located_in"]
            inspector_selected_node = st.session_state.get("explorer_selected_node", None)
            
            # Premium Rich Warm Palette
            palette = {
                "Equipment": "#3E6B7A",
                "Procedure": "#6B8E7B",
                "Hazard": "#A44A3F",
                "Sensor": "#D58936",
                "Document": "#755C6A",
                "Tool": "#4A7C75",
                "Material": "#8A7B61",
                "Location": "#5A6B8A",
                "Maintenance Action": "#C0703B",
                "Context Entity": "#A8A39D"
            }
            
            rendered_nodes_count = 0
            
            for node, data in subgraph.nodes(data=True):
                raw_type = data.get("type", "Entity Record")
                shape = "dot"
                mapped_type = "Context Entity"
                lower_type = str(raw_type).lower()
                
                if "chunk" in lower_type or "document" in lower_type: mapped_type, shape = "Document", "box"
                elif "equip" in lower_type or "part" in lower_type: mapped_type, shape = "Equipment", "database"
                elif "proced" in lower_type or "step" in lower_type: mapped_type, shape = "Procedure", "hexagon"
                elif "hazard" in lower_type or "risk" in lower_type: mapped_type, shape = "Hazard", "triangle"
                elif "action" in lower_type or "maint" in lower_type: mapped_type, shape = "Maintenance Action", "star"
                elif "sensor" in lower_type or "diag" in lower_type: mapped_type, shape = "Sensor", "diamond"
                    
                if mapped_type not in selected_categories:
                    continue
                    
                rendered_nodes_count += 1
                color_hex = palette.get(mapped_type, "#A8A39D")
                
                is_active = node in active_path_nodes if show_path else True
                is_inspected = node == inspector_selected_node
                
                # Minimum opacity increased so graph doesn't vanish entirely
                opacity = "1.0" if (is_active or is_inspected) else "0.45"
                h = color_hex.lstrip('#')
                r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                color_rgba = f"rgba({r},{g},{b},{opacity})"
                
                border_color = f"rgba(117, 85, 59, {opacity})"
                border_width = 1.5
                shadow = False
                
                if is_active and show_path:
                    # Terracotta Logic Path Focus
                    border_color = "#C0703B"
                    border_width = 4
                    shadow = {'enabled': True, 'color': 'rgba(192, 112, 59, 0.4)', 'size': 20, 'x': 0, 'y': 0}
                    
                if is_inspected:
                    # Deep Teal Inspected Node
                    color_rgba = "#3E6B7A"
                    border_color = "#1F3B4D"
                    border_width = 6
                    shadow = {'enabled': True, 'color': 'rgba(62, 107, 122, 0.6)', 'size': 30, 'x': 0, 'y': 0}
                
                # Generate strict, human-readable semantic label
                label = generate_semantic_label(node, data, meta_df)
                if len(label) > 25: 
                    label = label[:25] + "..."
                    
                connected_count = subgraph.degree(node)
                importance = round(connected_count / max(1, subgraph.number_of_nodes()), 2)
                
                # Nodes stay slightly smaller so edges don't tangle
                base_size = 14
                if is_active and show_path: base_size = 20
                if is_inspected: base_size = 32
                
                title = f"Entity: {label}\nCategory: {mapped_type}\nImportance: {importance}\n"
                
                net.add_node(
                    node, 
                    label=label, 
                    title=title, 
                    color={"background": color_rgba, "border": border_color, "highlight": {"background": "#D88C51", "border": "#3E3228"}}, 
                    borderWidth=border_width,
                    shape=shape,
                    size=base_size,
                    shadow=shadow,
                    # Thick white halo makes text extremely readable over dense lines
                    font={'size': 18 if is_inspected else (15 if is_active else 0), 'color': '#3E3228', 'strokeWidth': 5, 'strokeColor': '#FDFBF7'}
                )
                
            rendered_edges_count = 0
            for source, target, data in subgraph.edges(data=True):
                if source not in net.get_nodes() or target not in net.get_nodes():
                    continue
                    
                rendered_edges_count += 1
                    
                raw_rel = data.get("type", "related")
                if raw_rel == "related":
                    hash_val = hash(str(source) + str(target))
                    rel = edge_labels_map[hash_val % len(edge_labels_map)]
                else:
                    rel = raw_rel
                    
                is_active_edge = (source in active_path_nodes and target in active_path_nodes) if show_path else True
                is_inspected_edge = (source == inspector_selected_node or target == inspector_selected_node)
                
                if is_inspected_edge:
                    edge_color = "#3E6B7A"  # Teal
                    width = 6
                    font_size = 15
                    shadow = {'enabled': True, 'color': 'rgba(62, 107, 122, 0.5)', 'size': 12}
                elif is_active_edge and show_path:
                    edge_color = "#C0703B"  # Terracotta
                    width = 4
                    font_size = 13
                    shadow = {'enabled': True, 'color': 'rgba(192, 112, 59, 0.4)', 'size': 10}
                elif is_active_edge and not show_path:
                    edge_color = "rgba(117, 85, 59, 0.5)" # Stronger Brown
                    width = 2
                    font_size = 12
                    shadow = False
                else:
                    edge_color = "rgba(117, 85, 59, 0.15)" # Faint background brown
                    width = 0.5
                    font_size = 0 
                    shadow = False
                    
                net.add_edge(
                    source, 
                    target, 
                    title=rel, 
                    label=rel if font_size > 0 else "", 
                    color={"color": edge_color, "highlight": "#D88C51"}, 
                    width=width, 
                    shadow=shadow,
                    font={'size': font_size, 'align': 'middle', 'color': '#3E3228', 'strokeWidth': 4, 'strokeColor': '#FDFBF7'}
                )

            # MASSIVE UNTANGLING LOGIC: Extreme repulsion to spread nodes perfectly
            net.set_options("""
            var options = {
              "physics": {
                "barnesHut": {
                  "gravitationalConstant": -10000,
                  "centralGravity": 0.1,
                  "springLength": 450,
                  "springConstant": 0.05,
                  "damping": 0.09,
                  "avoidOverlap": 1
                },
                "minVelocity": 0.75,
                "solver": "barnesHut"
              },
              "interaction": {
                "hover": true,
                "tooltipDelay": 150,
                "zoomView": true,
                "dragView": true
              },
              "edges": {
                "smooth": {
                  "type": "continuous",
                  "forceDirection": "none",
                  "roundness": 0.5
                }
              }
            }
            """)

            html_string = net.generate_html()
            
            possible_edges = rendered_nodes_count * (rendered_nodes_count - 1)
            density_val = round((rendered_edges_count / possible_edges) * 100, 2) if possible_edges > 0 else 0
            
            html_string = inject_glass_ui(html_string, rendered_nodes_count, rendered_edges_count, density_val)
            
            with st.container(border=True):
                components.html(html_string, height=800)
            
        except ImportError:
            st.error("PyVis is not installed. Run `pip install pyvis` to enable interactive graphs.")
            render_placeholder(height=800)
