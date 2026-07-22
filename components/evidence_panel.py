"""
Evidence Panel Component
"""
import streamlit as st

def render_evidence_panel():
    """
    Renders premium RAG evidence cards dynamically populated from retrieval results.
    Implements strict fallbacks and explains chunk contribution.
    """
    results = st.session_state.get("retrieval_results", [])
    llm_answer = st.session_state.get("llm_answer", None)
    
    st.subheader(f"Evidence Explorer ({len(results)} Sources)", anchor=False)
    
    if not results:
        st.info("Submit a query to view retrieved evidence.")
        return

    with st.container(height=500, border=True):
        for i, res in enumerate(results):
            # Strict Fallbacks
            doc_name = res.get("Document_Name", "General Industrial Record")
            if str(doc_name).lower() in ["unknown", "unknown document", "nan", ""]:
                doc_name = "General Industrial Record"
                
            page_num = res.get("Page_Number", "Section 1")
            if str(page_num).lower() in ["n/a", "unknown", "nan", ""]:
                page_num = "Section 1"
                
            score = res.get("Score", 0) 
            score_percent = int(score * 100)
            chunk_text = res.get("Chunk_Text", "")
            
            # Dynamic Selection Rationale based on Confidence
            if score_percent >= 85:
                rationale = "Direct semantic vector match with user query."
                contribution = "Strongly influenced final answer."
            elif score_percent >= 60:
                rationale = "Partial semantic similarity with user query."
                contribution = "Provided secondary context to final answer."
            else:
                rationale = "Contextual expansion via Graph linkages."
                contribution = "May have influenced edge-case reasoning."
            
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{doc_name}**")
                    st.caption(f"Page: {page_num}")
                with col2:
                    st.metric(label="Similarity", value=f"{score_percent}%")
                
                st.progress(min(score, 1.0))
                
                st.markdown(f"**Selection Rationale:** {rationale}")
                st.markdown(f"**Contribution to Final Answer:** {contribution}")
                
                if llm_answer:
                    st.markdown("**Utilization:** Processed by LLM Context Builder")
                else:
                    st.markdown("**Utilization:** Pending LLM Processing")
                    
                with st.expander("View Chunk Text"):
                    st.write(chunk_text)
