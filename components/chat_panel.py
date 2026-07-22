"""
Chat Panel Component
"""
import streamlit as st
import time
import json
import networkx as nx
from services.retrieval_service import search
from services.graph_service import get_subgraph
from services.llm_service import build_context, generate_answer, classify_intent, generate_smart_title
from services.investigation_service import create_investigation, add_message

def execute_pipeline(query: str):
    """Executes the full GraphRAG pipeline with progressive loading states."""
    if not query.strip() or st.session_state.get("is_processing", False):
        return
        
    st.session_state["is_processing"] = True
    
    history = st.session_state.get("investigation_history", [])
    memory_context = history[-4:] if len(history) >= 4 else history
    
    with st.status("Initializing Copilot...", expanded=True) as status:
        t0 = time.time()
        
        # 1. Semantic Retrieval
        status.update(label="Searching Knowledge Base...", state="running")
        t_search_start = time.time()
        results = search(query, top_k=5)
        t_search_end = time.time()
        
        # 2. Knowledge Graph Expansion
        status.update(label="Expanding Knowledge Graph...", state="running")
        t_graph_start = time.time()
        subgraph = get_subgraph(results, depth=1)
        t_graph_end = time.time()
        
        # 3. Context & Prompt Building
        status.update(label="Building Context...", state="running")
        context = build_context(results, subgraph)
        
        if not results:
            coverage = "Low"
            coverage_reason = "No relevant chunks found in the Knowledge Base."
        else:
            best_score = results[0]["Score"]
            if best_score > 1.2 or len(results) < 2:
                coverage = "Low"
                coverage_reason = f"Only weak matches found (Best Score: {best_score})."
            elif best_score < 0.8:
                coverage = "High"
                coverage_reason = f"Strong semantic matches found (Best Score: {best_score})."
            else:
                coverage = "Medium"
                coverage_reason = "Partial matches found, confidence is moderate."
                
        is_general_ai = st.session_state.get("general_ai_mode", False)
        
        if coverage == "Low" and not is_general_ai:
            status.update(label="Confidence Gate Triggered...", state="running")
            answer = "⚠️ **Confidence Gate Triggered**\n\nThe current knowledge base does not contain enough verified information to answer confidently.\n\n*Suggestions:*\n- Upload additional documents (e.g., Maintenance SOP, Repair Manual).\n- Enable **General AI Mode** below to allow external knowledge."
            llm_latency, tokens, intent = 0.0, 0, "Blocked"
            llm_metadata = {}
        else:
            status.update(label="Generating AI Response...", state="running")
            answer, llm_latency, tokens, intent, llm_metadata = generate_answer(context, query, is_general_ai, memory_context)
            if coverage == "Medium" and not is_general_ai:
                answer = "⚠️ *Warning: Limited supporting evidence in the knowledge base.* \n\n" + answer
        
        status.update(label="Finalizing Investigation...", state="complete", expanded=False)
        t1 = time.time()
        
        # Determine Current Investigation ID
        if not st.session_state.get("current_investigation_id"):
            title = generate_smart_title(query)
            st.session_state["current_investigation_id"] = create_investigation(title)
            
        inv_id = st.session_state["current_investigation_id"]
        
        # Build comprehensive pipeline_metrics object
        pipeline_metrics = {
            "pipeline_time": round(t1 - t0, 2),
            "retrieval_time": round(t_search_end - t_search_start, 3),
            "graph_time": round(t_graph_end - t_graph_start, 3),
            "llm_time": llm_latency,
            "prompt_time": 0.0, # Negligible locally
            "prompt_tokens": llm_metadata.get("prompt_tokens", 0) if 'llm_metadata' in locals() else 0,
            "completion_tokens": llm_metadata.get("completion_tokens", 0) if 'llm_metadata' in locals() else 0,
            "total_tokens": tokens,
            "retrieved_chunks": len(results) if results else 0,
            "retrieved_documents": len(set([r.get("Document_Name", "Unknown") for r in results])) if results else 0,
            "graph_nodes": subgraph.number_of_nodes() if subgraph else 0,
            "graph_edges": subgraph.number_of_edges() if subgraph else 0,
            "context_length": llm_metadata.get("context_length", 0) if 'llm_metadata' in locals() else 0,
            "prompt_length": llm_metadata.get("prompt_length", 0) if 'llm_metadata' in locals() else 0,
            "confidence": coverage,
            "finish_reason": llm_metadata.get("finish_reason", "Unknown") if 'llm_metadata' in locals() else "Unknown",
            "model_name": llm_metadata.get("model_name", "google/gemini-2.5-flash") if 'llm_metadata' in locals() else "google/gemini-2.5-flash"
        }
        
        # Save to SQLite
        results_json = json.dumps(results) if results else "[]"
        subgraph_json = json.dumps(nx.node_link_data(subgraph)) if subgraph else "{}"
        metrics_json = json.dumps(pipeline_metrics)
        
        add_message(inv_id, query, intent, answer, results_json, subgraph_json, metrics_json, coverage, coverage_reason)
        
        # Append to visual history
        st.session_state["investigation_history"].append({
            "query": query,
            "intent": intent,
            "answer": answer,
            "results": results,
            "subgraph": subgraph,
            "coverage": coverage,
            "coverage_reason": coverage_reason,
            "general_ai_mode": is_general_ai,
            "pipeline_metrics": pipeline_metrics
        })
        
        # Update top-level legacy states for other panels
        st.session_state["pipeline_metrics"] = pipeline_metrics
        st.session_state["retrieval_results"] = results
        st.session_state["retrieved_subgraph"] = subgraph
        st.session_state["llm_answer"] = answer
        st.session_state["query_intent"] = intent
        st.session_state["coverage"] = coverage
        st.session_state["coverage_reason"] = coverage_reason
        
    st.session_state["is_processing"] = False
    
    if "user_input" in st.session_state:
        st.session_state["user_input"] = ""

def extract_main_answer_and_extras(full_answer: str):
    main_body = full_answer
    followups = []
    topics = []
    
    parts = full_answer.split("### Follow-up Questions")
    if len(parts) == 2:
        main_body = parts[0].strip()
        rest = parts[1].split("### Explore Related Topics")
        followups_raw = rest[0].strip()
        followups = [line.strip("- *").strip() for line in followups_raw.split("\n") if line.strip()]
        
        if len(rest) == 2:
            topics_raw = rest[1].strip()
            topics = [line.strip("- *").strip() for line in topics_raw.split("\n") if line.strip()]

    # DIAGNOSTICS LOGGING
    import datetime
    try:
        with open("data/deployment_debug.log", "a", encoding="utf-8") as f:
            f.write(f"\\n--- [RENDERING DIAGNOSTICS] {datetime.datetime.now()} ---\\n")
            f.write(f"Raw Markdown Returned:\\n{full_answer}\\n")
            f.write(f"Parsed Main Body:\\n{main_body}\\n")
            f.write(f"Parsed Follow-ups: {followups}\\n")
            f.write(f"Parsed Topics: {topics}\\n")
    except Exception:
        pass
            
    return main_body, followups, topics

def set_query(query: str):
    st.session_state["user_input"] = query

def submit_query():
    query = st.session_state.get("user_input", "")
    if query.strip():
        execute_pipeline(query)

def render_chat_panel():
    if "investigation_history" not in st.session_state:
        st.session_state["investigation_history"] = []
    if "current_investigation_id" not in st.session_state:
        st.session_state["current_investigation_id"] = None
    if "is_processing" not in st.session_state:
        st.session_state["is_processing"] = False
    if "general_ai_mode" not in st.session_state:
        st.session_state["general_ai_mode"] = False
        
    if "user_input" not in st.session_state:
        st.session_state["user_input"] = ""

    with st.container(border=True):
        st.markdown("""
        <div id='main-chat-container-marker' style='display:none;'></div>
        <img src="empty.gif" onerror="
            setTimeout(() => {
                const marker = document.getElementById('main-chat-container-marker');
                if (marker) {
                    let wrapper = marker.closest('[data-testid=\\'stVerticalBlockBorderWrapper\\']');
                    if (!wrapper) wrapper = marker.parentElement.parentElement.parentElement;
                    if (wrapper && !wrapper.classList.contains('copilot-premium')) {
                        wrapper.classList.add('copilot-premium');
                    }
                }
            }, 50);
        " style="display:none;">
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div style="background: linear-gradient(135deg, #D88C51, #C0703B); color: white; border-radius: 12px; padding: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(216, 140, 81, 0.3);">
                <span class="material-symbols-rounded" style="font-size: 24px;">psychology</span>
            </div>
            <div>
                <h2 style="margin: 0; padding: 0; font-size: 1.5rem; font-weight: 700; color: #3E3228;">NEXUS AI Copilot</h2>
                <div style="font-size: 0.85rem; color: #75553B; font-weight: 500; letter-spacing: 0.5px;">
                    Enterprise Investigation Workspace | Grounded Answers • Conversational Memory
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        is_busy = st.session_state["is_processing"]
        
        if is_busy:
            st.markdown("""
            <style>
            @keyframes pageBreathing {
                0% { opacity: 1; filter: brightness(1); }
                50% { opacity: 0.85; filter: brightness(0.85); }
                100% { opacity: 1; filter: brightness(1); }
            }
            .stApp {
                animation: pageBreathing 4s infinite ease-in-out !important;
            }
            </style>
            """, unsafe_allow_html=True)
        
        with st.container(border=False):
            if not st.session_state["investigation_history"]:
                st.markdown("""
                <div style='text-align: center; margin-top: 50px; color: #75553B;'>
                    <hr style='width: 50%; margin: 0 auto 20px auto; border-color: rgba(216, 140, 81, 0.3);'>
                    <h3 style='color: #3E3228;'>Welcome to NEXUS AI</h3>
                    <p style='font-size: 1.1rem;'>Start a new engineering investigation or continue a previous one.<br>Your investigations are automatically saved and organized.</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📖 Quick Start Guide", expanded=False):
                    st.markdown("""
                    1. **Ask a Question**: Type your query below.
                    2. **Review Evidence**: Check the Evidence panel.
                    3. **Explore Connections**: Open the Knowledge Explorer to analyze the graph.
                    """)
                    
                st.write("**Suggested Questions:**")
                st.button("Summarize maintenance SOP", disabled=is_busy, on_click=set_query, args=("Summarize maintenance SOP",))
                st.button("Emergency Shutdown Analysis", disabled=is_busy, on_click=set_query, args=("Emergency Shutdown Analysis",))
            else:
                for idx, turn in enumerate(st.session_state["investigation_history"]):
                    is_last = (idx == len(st.session_state["investigation_history"]) - 1)
                    
                    with st.chat_message("user"):
                        st.write(turn["query"])
                        
                    with st.chat_message("assistant"):
                        st.caption(f"**Intent Detected:** {turn.get('intent', 'General')}")
                        main_answer, followups, topics = extract_main_answer_and_extras(turn["answer"])
                        st.write(main_answer)
                        
                        cols = st.columns(4)
                        if turn.get("results") and len(turn["results"]) > 0:
                            cols[0].caption("✅ Grounded")
                        if turn.get("subgraph") and turn["subgraph"].number_of_edges() > 0:
                            cols[1].caption("🔗 Graph Supported")
                        if turn.get("general_ai_mode"):
                            cols[2].caption("🌐 General AI Mode")
                        else:
                            cols[2].caption("🛡️ Strict KB Mode")
                            
                        cov = turn.get("coverage", "Unknown")
                        color = "red" if cov == "Low" else "orange" if cov == "Medium" else "green"
                        cols[3].markdown(f"<span style='color:{color}; font-size: 0.8rem;'>Coverage: {cov}</span>", unsafe_allow_html=True)
                        
                        if is_last:
                            if followups or topics:
                                st.divider()
                            if followups:
                                st.write("**Follow-up Questions:**")
                                for q in followups:
                                    if q: st.button(q, disabled=is_busy, key=f"fq_{q}", on_click=set_query, args=(q,))
                            if topics:
                                st.write("**Explore Related Topics:**")
                                for t in topics:
                                    if t: st.button(t, disabled=is_busy, key=f"rt_{t}", on_click=set_query, args=(t,))
        
        st.write("---") 
        st.toggle("🌐 Enable General AI Mode (Hybrid KB + World Knowledge)", key="general_ai_mode", disabled=is_busy)
        
        if st.session_state.get("general_ai_mode", False):
            st.caption("🟢 **Current Mode:** General AI (Using Knowledge Base + External Knowledge)")
        else:
            st.caption("🛡️ **Current Mode:** Strict Enterprise (Restricted to Knowledge Base Only)")
            
    # Natively sticky chat input at the bottom of the scrollable main layout
    if prompt := st.chat_input("Message NEXUS...", key="user_input_chat", disabled=is_busy):
        # We manually process it since the user pressed enter
        set_query(prompt)
        execute_pipeline(prompt)
        st.rerun()
