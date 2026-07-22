"""
Status Bar / Live Data Pipeline Component
"""
import streamlit as st

def render_status_bar():
    """
    Renders the live data pipeline sequence using native Streamlit columns.
    """
    # Determine current active steps based on session state
    has_results = bool(st.session_state.get("retrieval_results"))
    has_graph = st.session_state.get("retrieved_subgraph") is not None
    has_llm = bool(st.session_state.get("llm_answer"))
    
    st.write("**Live Pipeline Status:**")
    
    with st.container(border=True):
        cols = st.columns(5)
        
        # Step 1: User Query (Always active if this renders)
        with cols[0]:
            st.write("👤 Query" if has_results else "👤 Waiting")
            if has_results:
                st.success("OK")
            else:
                st.info("...")
                
        # Step 2: Semantic Search
        with cols[1]:
            st.write("🔍 Search")
            if has_results:
                st.success("FAISS")
            else:
                st.info("...")
                
        # Step 3: Graph Expansion
        with cols[2]:
            st.write("🕸️ Graph")
            if has_graph:
                st.success("Expanded")
            else:
                st.info("...")
                
        # Step 4: Context Building
        with cols[3]:
            st.write("🏗️ Context")
            if has_llm:
                st.success("Built")
            else:
                st.info("...")
                
        # Step 5: LLM Generation
        with cols[4]:
            st.write("🤖 LLM")
            if has_llm:
                st.success("Complete")
            else:
                st.info("...")
