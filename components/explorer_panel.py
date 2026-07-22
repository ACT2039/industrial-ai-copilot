"""
Knowledge Explorer Panel Component
"""
import streamlit as st
import networkx as nx
from services.retrieval_service import load_metadata_and_chunks
from services.graph_service import generate_semantic_label

def render_explorer_panel():
    """
    Renders the dedicated side panel for the full-screen Knowledge Explorer.
    """
    subgraph = st.session_state.get("retrieved_subgraph")
    meta_df, _ = load_metadata_and_chunks()
    
    st.subheader("Knowledge Summary", anchor=False)
    
    if not subgraph or subgraph.number_of_nodes() == 0:
        st.info("Retrieve knowledge to explore entities.")
        return
        
    with st.container(border=True):
        total_nodes = subgraph.number_of_nodes()
        total_edges = subgraph.number_of_edges()
        
        # Calculate dynamic metrics
        degrees = dict(subgraph.degree())
        highest_degree_node = max(degrees, key=degrees.get) if degrees else "None"
        
        # Density
        possible_edges = total_nodes * (total_nodes - 1)
        density = round((total_edges / possible_edges) * 100, 2) if possible_edges > 0 else 0
        
        avg_connections = round(sum(degrees.values()) / max(1, len(degrees)), 1)
        
        # We enforce ID masking here too using the semantic generator
        if highest_degree_node != "None":
            highest_degree_data = subgraph.nodes[highest_degree_node] if highest_degree_node in subgraph else {}
            highest_degree_node_display = generate_semantic_label(highest_degree_node, highest_degree_data, meta_df)[:25]
        else:
            highest_degree_node_display = "None"
            
        st.metric("Total Entities", total_nodes)
        st.metric("Total Relationships", total_edges)
        st.metric("Graph Density", f"{density}%")
        st.metric("Average Connections", avg_connections)
        st.metric("Most Connected Entity", highest_degree_node_display)
        
    st.divider()
    
    st.subheader("Entity Inspector", anchor=False)
    
    # Entity Search Control
    nodes_list = list(subgraph.nodes())
    # Clean the list for display
    display_names = []
    node_mapping = {}
    for n in nodes_list:
        data = subgraph.nodes[n]
        name = generate_semantic_label(n, data, meta_df)
        
        # Handle duplicates by appending a unique counter if needed, but dict mapping works via last-in.
        # Actually better to map ID to name, but selectbox needs unique options.
        if name in node_mapping:
            name = f"{name} (Secondary)"
            
        display_names.append(name)
        node_mapping[name] = n
        
    selected_name = st.selectbox("Search & Inspect Entity", options=["-- Select Entity --"] + display_names)
    
    if selected_name != "-- Select Entity --":
        selected_node = node_mapping[selected_name]
        st.session_state["explorer_selected_node"] = selected_node
        
        # Render the Enterprise Node Information Panel
        with st.container(border=True):
            data = subgraph.nodes[selected_node]
            raw_type = data.get("type", "Entity Record")
            
            # Map type safely
            mapped_type = "Context Entity"
            lower_type = str(raw_type).lower()
            if "chunk" in lower_type or "document" in lower_type: mapped_type = "Document"
            elif "equip" in lower_type or "part" in lower_type: mapped_type = "Equipment"
            elif "proced" in lower_type or "step" in lower_type: mapped_type = "Procedure"
            elif "hazard" in lower_type or "risk" in lower_type: mapped_type = "Hazard"
            elif "action" in lower_type or "maint" in lower_type: mapped_type = "Maintenance Action"
            elif "sensor" in lower_type or "diag" in lower_type: mapped_type = "Sensor"
            
            st.write(f"**Name:** {selected_name}")
            st.write(f"**Category:** {mapped_type}")
            st.write(f"**Description:** Internal {mapped_type} Record")
            
            # Connected logic
            neighbors = list(subgraph.neighbors(selected_node))
            st.write(f"**Connected Entities:** {len(neighbors)}")
            
            importance = round(len(neighbors) / max(1, total_nodes), 2)
            st.write(f"**Importance Score:** {importance}")
            
            st.progress(importance)
            
            if neighbors:
                with st.expander("View Connections"):
                    for nb in neighbors[:10]:
                        nb_data = subgraph.nodes[nb] if nb in subgraph else {}
                        nb_name = generate_semantic_label(nb, nb_data, meta_df)
                        st.caption(f"- {nb_name}")
                    if len(neighbors) > 10:
                        st.caption("... and more")
    else:
        st.session_state["explorer_selected_node"] = None
        st.info("Select an entity to view deep metadata and connections.")
