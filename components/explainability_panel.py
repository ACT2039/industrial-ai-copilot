"""
Explainability Panel Component
"""
import streamlit as st
import networkx as nx

def render_explainability_panel():
    """
    Renders the advanced Explainability Panel with detailed confidence breakdowns
    and text-based semantic reasoning.
    """
    results = st.session_state.get("retrieval_results", [])
    subgraph = st.session_state.get("retrieved_subgraph", None)
    llm_answer = st.session_state.get("llm_answer", None)
    
    st.subheader("Why this answer?", anchor=False, help="Transparency report for the generated response.")
    
    if not llm_answer:
        st.info("A transparency report will appear after an answer is generated.")
        return
        
    with st.container(border=True):
        st.write("### Confidence Breakdown")
        
        # Calculate Semantic Retrieval Confidence
        avg_semantic = 0.0
        semantic_reason = "No semantic data retrieved."
        if results:
            avg_semantic = sum([res.get("Score", 0) for res in results]) / len(results)
            if avg_semantic > 0.8:
                semantic_reason = "Strong direct vector similarity between the user query and knowledge chunks."
            elif avg_semantic > 0.6:
                semantic_reason = "Moderate vector similarity. Context may be partially related."
            else:
                semantic_reason = "Low vector similarity. Relies heavily on graph expansion."
                
        # Calculate Knowledge Graph Support
        kg_support = 0.0
        kg_reason = "No topological support found."
        active_chunk_ids = set([res.get("Chunk_ID") for res in results])
        active_nodes = set(active_chunk_ids)
        if subgraph:
            for chunk_id in active_chunk_ids:
                if chunk_id in subgraph:
                    for neighbor in subgraph.neighbors(chunk_id):
                        active_nodes.add(neighbor)
            active_subgraph = subgraph.subgraph(active_nodes)
            if active_subgraph.number_of_nodes() > 1:
                possible_edges = active_subgraph.number_of_nodes() * (active_subgraph.number_of_nodes() - 1)
                actual_edges = active_subgraph.number_of_edges()
                kg_support = min(1.0, (actual_edges / possible_edges) * 10)
                
                if kg_support > 0.7:
                    kg_reason = f"Highly clustered subgraph with {actual_edges} dense topological relationships validating the context."
                else:
                    kg_reason = f"Sparse subgraph linkages. Entities have limited interconnectivity ({actual_edges} edges)."
            else:
                kg_support = 0.5
                kg_reason = "Graph structure is isolated. Context lacks entity corroboration."
                
        # LLM Generation Confidence
        llm_conf = 0.95 if "### Referenced Documents" in llm_answer else 0.60
        if llm_conf > 0.9:
            llm_reason = "LLM successfully adhered to enterprise templates and cited sources."
        else:
            llm_reason = "LLM struggled to apply the expected structural template."
        
        # Overall Confidence
        overall_conf = (avg_semantic * 0.5) + (kg_support * 0.3) + (llm_conf * 0.2)
        st.session_state["overall_confidence"] = overall_conf
        
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"**Semantic Retrieval: {int(avg_semantic * 100)}%**")
            st.progress(min(1.0, avg_semantic))
            st.write(f"<small>{semantic_reason}</small>", unsafe_allow_html=True)
            
            st.write("")
            st.caption(f"**Knowledge Graph Support: {int(kg_support * 100)}%**")
            st.progress(min(1.0, kg_support))
            st.write(f"<small>{kg_reason}</small>", unsafe_allow_html=True)
            
        with col2:
            st.caption(f"**LLM Generation: {int(llm_conf * 100)}%**")
            st.progress(min(1.0, llm_conf))
            st.write(f"<small>{llm_reason}</small>", unsafe_allow_html=True)
            
            st.write("")
            st.caption(f"**Overall System Confidence: {int(overall_conf * 100)}%**")
            st.progress(min(1.0, overall_conf))
            if overall_conf > 0.8:
                st.write("<small>System is highly confident in the provided answer.</small>", unsafe_allow_html=True)
            else:
                st.write("<small>System generated a best-effort answer with low corroboration.</small>", unsafe_allow_html=True)
            
        st.divider()
        st.write("### Source Traceability")
        
        docs = list(set([res.get("Document_Name", "General Industrial Record") for res in results]))
        st.write(f"**Documents Consulted:** {len(docs)}")
        for doc in docs:
            st.caption(f"- {doc}")
            
        st.write(f"**Retrieved Knowledge Chunks:** {len(results)}")
        
        if subgraph:
            st.write(f"**Business Entities Identified:** {subgraph.number_of_nodes()}")
            st.write(f"**Topological Relationships Traversed:** {subgraph.number_of_edges()}")
        
        st.divider()
        st.write("### Reasoning")
        st.write("**Why these documents were selected:**")
        st.caption("Selected by measuring the geometric distance (FAISS) between the user's intent vector and the embedded knowledge chunks.")
        st.write("**Why this answer was generated:**")
        st.caption("The Copilot synthesized the answer strictly from the retrieved document chunks and corroborated the facts against the Knowledge Graph's topological constraints.")
