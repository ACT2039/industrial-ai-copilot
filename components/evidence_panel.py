"""
Evidence Panel Component
"""
import streamlit as st

def render_evidence_panel():
    """
    Renders premium RAG evidence cards dynamically populated from retrieval results.
    """
    results = st.session_state.get("retrieval_results", [])
    
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3 style="margin: 0; color: #f8fafc; font-size: 1.2rem; font-weight: 600;">Evidence Explorer</h3>
            <span class="chip chip-green" style="font-size: 0.7rem;">{len(results)} Sources Retrieved</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if not results:
        st.info("Submit a query to view retrieved evidence.")
        return

    # Use a scrollable container for evidence cards
    with st.container(height=300, border=False):
        for i, res in enumerate(results):
            # Alternate border colors for premium aesthetic
            border_color = "#38bdf8" if i % 2 == 0 else "#818cf8"
            
            doc_name = res.get("Document_Name", "Unknown Document")
            score_percent = int(res.get("Score", 0) * 100) # Assuming score is normalized cosine similarity ~0-1
            chunk_id = res.get("Chunk_ID", "N/A")
            page_num = res.get("Page_Number", "N/A")
            chunk_text = res.get("Chunk_Text", "")
            
            # Truncate text for preview
            preview_length = 200
            preview_text = chunk_text[:preview_length] + "..." if len(chunk_text) > preview_length else chunk_text
            
            # Confidence rating mapping
            if score_percent > 85: confidence = "High"
            elif score_percent > 65: confidence = "Medium"
            else: confidence = "Low"
            
            card_html = f"""
            <div style="background: rgba(15,23,42,0.6); border-left: 4px solid {border_color}; border-radius: 8px; padding: 16px; margin-bottom: 16px; border-right: 1px solid rgba(255,255,255,0.05); border-top: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                    <div>
                        <div style="color: #e2e8f0; font-weight: 600; font-size: 1rem; margin-bottom: 4px; word-break: break-word;">{doc_name}</div>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                            <span class="chip" style="font-size: 0.7rem; padding: 2px 8px; border-color: rgba(255,255,255,0.1); color: #cbd5e1;">ID: {chunk_id}</span>
                            <span class="chip" style="font-size: 0.7rem; padding: 2px 8px; border-color: rgba(255,255,255,0.1); color: #cbd5e1;">Page: {page_num}</span>
                        </div>
                    </div>
                    <div style="text-align: right; min-width: 60px;">
                        <div style="color: #10b981; font-weight: 700; font-size: 1.1rem;">{score_percent}%</div>
                        <div style="color: #64748b; font-size: 0.7rem; text-transform: uppercase;">Similarity</div>
                    </div>
                </div>
                
                <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.02); color: #94a3b8; font-size: 0.85rem; line-height: 1.4;">
                    {preview_text}
                </div>
                
                <div style="display: flex; justify-content: space-between; margin-top: 10px; font-size: 0.75rem; color: #64748b;">
                    <span>Confidence: {confidence}</span>
                    <span style="color: {border_color};">Rank {res.get('Rank', i+1)}</span>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
