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

def generate_semantic_label(node_id: str, node_data: dict, meta_df=None) -> str:
    """
    Generates a human-readable semantic label for any graph node, 
    ensuring internal backend IDs (e.g., CHUNK025651) are NEVER exposed.
    Priority: 1. Extracted Entity Name, 2. Document Title, 3. Chunk Summary.
    """
    nid = str(node_id).strip()
    raw_type = node_data.get("type", "Entity Record")
    lower_nid = nid.lower()
    
    # 1. Handle Chunks
    if "chunk" in lower_nid or "chk" in lower_nid or raw_type == "Chunk":
        # Try to resolve document title from metadata
        if meta_df is not None:
            matches = meta_df[meta_df["Chunk_ID"] == nid]
            if not matches.empty:
                doc_name = matches.iloc[0].get("File_Name", "General Record")
                doc_name = str(doc_name).replace(".pdf", "").replace(".txt", "").replace(".csv", "")
                if doc_name.lower() not in ["unknown", "unknown document", "nan", ""]:
                    return doc_name
                    
        # Fallback to generating a Semantic Title from the text content
        text = str(node_data.get("text", "")).strip()
        if text and len(text) > 10:
            words = text.split()
            # Grab first 4 words to form a pseudo-title, capitalize them
            title_words = [w.capitalize() for w in words[:4] if w.isalpha() or w.isalnum()]
            if title_words:
                return " ".join(title_words)
                
        return "Knowledge Segment"
        
    # 2. Handle Documents
    if "doc" in lower_nid:
        return "Source Document"
        
    # 3. Generic Entity cleanup
    if "entity" in lower_nid:
        return "Extracted Entity"
        
    # 4. Mask UUIDs or super long IDs
    if len(nid) > 30:
        return "System Entity"
        
    # 5. Business Concept / Extracted Entity
    # Clean up standard entities by applying title case if they are entirely lowercase
    if nid.islower():
        return nid.title()
        
    return nid

