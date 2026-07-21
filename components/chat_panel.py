"""
Chat Panel Component
"""
import streamlit as st
import time
from services.retrieval_service import search
from services.graph_service import get_subgraph
from services.llm_service import build_context, generate_answer

def render_chat_panel():
    """
    Renders the enterprise AI chat panel, handling the full end-to-end GraphRAG pipeline.
    """
    # Initialize states
    if "retrieval_results" not in st.session_state:
        st.session_state["retrieval_results"] = []
    if "search_time" not in st.session_state:
        st.session_state["search_time"] = 0.0
    if "llm_answer" not in st.session_state:
        st.session_state["llm_answer"] = None
    if "llm_time" not in st.session_state:
        st.session_state["llm_time"] = 0.0
    if "total_time" not in st.session_state:
        st.session_state["total_time"] = 0.0
    if "tokens_used" not in st.session_state:
        st.session_state["tokens_used"] = 0

    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h2 style="margin: 0; color: #f8fafc; font-size: 1.5rem; font-weight: 600;">NEXUS AI</h2>
            <span class="chip" style="font-size: 0.7rem; border-color: rgba(56,189,248,0.3); color: #38bdf8;">Enterprise Copilot</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Scrollable container for conversation/welcome
    with st.container(height=380, border=False):
        if not st.session_state["llm_answer"]:
            # Display Welcome State
            st.markdown(
                """
                <p style="color: #94a3b8; font-size: 1rem; margin-bottom: 25px;">Ask intelligent questions across your enterprise knowledge base.</p>
                <div style="color: #64748b; font-size: 0.8rem; text-transform: uppercase; font-weight: 600; letter-spacing: 1px; margin-bottom: 10px;">Suggested Questions</div>
                <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px;">
                    <div style="padding: 12px 16px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; color: #cbd5e1; font-size: 0.9rem;">
                        • Summarize maintenance SOP
                    </div>
                    <div style="padding: 12px 16px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; color: #cbd5e1; font-size: 0.9rem;">
                        • Explain transformer architecture
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            # Display Generated Response State
            st.markdown(
                f"""
                <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px 12px 0 12px; padding: 15px; margin-bottom: 15px; color: #e2e8f0; text-align: right; margin-left: 20%;">
                    {st.session_state.get('last_query', '')}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown(
                """
                <div style="background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 12px 12px 12px 0; padding: 15px; margin-bottom: 10px; color: #f1f5f9; margin-right: 10%;">
                """,
                unsafe_allow_html=True
            )
            st.markdown(st.session_state["llm_answer"])
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown(
                f"""
                <div style="display: flex; justify-content: flex-end; gap: 10px; margin-bottom: 20px;">
                    <span style="color: #64748b; font-size: 0.75rem;">Pipeline Latency: {st.session_state['total_time']}s | LLM Tokens: {st.session_state['tokens_used']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Input Form
    with st.form(key="search_form", clear_on_submit=True):
        query = st.text_input("Message NEXUS...", placeholder="Ask anything about your data...", label_visibility="collapsed")
        submit_button = st.form_submit_button("Send Query", use_container_width=True)
        
        if submit_button and query.strip():
            with st.spinner("Executing GraphRAG Pipeline..."):
                t0 = time.time()
                
                # 1. Semantic Retrieval
                t_search_start = time.time()
                results = search(query, top_k=5)
                t_search_end = time.time()
                
                # 2. Knowledge Graph Expansion
                subgraph = get_subgraph(results, depth=1)
                
                # 3. Context & Prompt Building
                context = build_context(results, subgraph)
                
                # 4. LLM Generation
                answer, llm_latency, tokens = generate_answer(context, query)
                
                t1 = time.time()
                
                # 5. Store States
                st.session_state["retrieval_results"] = results
                st.session_state["search_time"] = round(t_search_end - t_search_start, 3)
                st.session_state["retrieved_subgraph"] = subgraph
                st.session_state["llm_answer"] = answer
                st.session_state["llm_time"] = llm_latency
                st.session_state["tokens_used"] = tokens
                st.session_state["total_time"] = round(t1 - t0, 2)
                st.session_state["last_query"] = query
                
                st.rerun()
