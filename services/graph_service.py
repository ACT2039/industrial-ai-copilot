"""
Graph Service

Handles the safe loading of the NetworkX Knowledge Graph,
and extracting ego subgraphs around retrieved chunks.
"""
import streamlit as st
import pickle
import networkx as nx
from services.config_service import ResourceLoader

@st.cache_resource(show_spinner=False)
def load_knowledge_graph():
    """
    Loads the Knowledge Graph (gpickle) into memory, cached per session.
    """
    try:
        kg_path = ResourceLoader.get_knowledge_graph_path()
        with open(kg_path, 'rb') as f:
            graph = pickle.load(f)
            
        if not isinstance(graph, nx.Graph) and not isinstance(graph, nx.DiGraph):
            raise ValueError("Loaded object is not a valid NetworkX Graph")
            
        return graph
    except Exception as e:
        st.error(f"Failed to load Knowledge Graph: {str(e)}")
        return None

def get_subgraph(retrieval_results: list, depth: int = 1):
    """
    Extracts a subgraph around the Chunk_IDs present in the retrieval results.
    """
    kg = load_knowledge_graph()
    if kg is None or not retrieval_results:
        return nx.Graph()
        
    subgraph = nx.Graph()
    chunk_ids = [res.get("Chunk_ID") for res in retrieval_results if res.get("Chunk_ID")]
    
    for chunk_id in chunk_ids:
        if kg.has_node(chunk_id):
            # Extract ego graph around the chunk
            ego = nx.ego_graph(kg, chunk_id, radius=depth)
            subgraph = nx.compose(subgraph, ego)
            
    return subgraph

def get_graph_statistics(graph):
    """
    Exposes safe graph statistics for the analytics panel.
    """
    if graph is None:
        return {"nodes": 0, "edges": 0}
        
    return {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges()
    }
