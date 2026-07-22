"""
Sidebar Component with Enterprise Investigation History
"""
import streamlit as st
import os
import json
import time
import datetime
import networkx as nx
from services.config_service import ResourceLoader
from services.investigation_service import (
    get_investigations, search_investigations, create_investigation,
    delete_investigation, update_investigation, get_messages
)
from components.header import clear_session

def start_new_investigation():
    """Resets the UI to an empty state for a new investigation."""
    keys_to_clear = [
        "investigation_history", "current_investigation_id", 
        "retrieval_results", "search_time", "llm_answer", "llm_time", 
        "total_time", "tokens_used", "last_query", "retrieved_subgraph",
        "query_intent", "coverage", "coverage_reason"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state["is_processing"] = False

def restore_investigation(inv_id):
    """Restores an investigation from SQLite into the live session state."""
    messages = get_messages(inv_id)
    if not messages:
        return
        
    st.session_state["current_investigation_id"] = inv_id
    
    # Rebuild history
    history = []
    for msg in messages:
        results = json.loads(msg["results_json"]) if msg["results_json"] else []
        try:
            subgraph_data = json.loads(msg["subgraph_json"]) if msg["subgraph_json"] else {}
            subgraph = nx.node_link_graph(subgraph_data) if subgraph_data else None
        except:
            subgraph = None
            
        try:
            metrics_data = json.loads(msg["metrics_json"]) if msg.get("metrics_json") else {}
        except:
            metrics_data = {}
            
        history.append({
            "query": msg["query"],
            "intent": msg["query_intent"],
            "answer": msg["llm_answer"],
            "results": results,
            "subgraph": subgraph,
            "coverage": msg["coverage"],
            "coverage_reason": msg["coverage_reason"],
            "pipeline_metrics": metrics_data
        })
        
    st.session_state["investigation_history"] = history
    
    # Restore latest state for cross-panel compatibility
    latest = history[-1]
    st.session_state["retrieval_results"] = latest["results"]
    st.session_state["retrieved_subgraph"] = latest["subgraph"]
    st.session_state["llm_answer"] = latest["answer"]
    st.session_state["query_intent"] = latest["intent"]
    st.session_state["coverage"] = latest["coverage"]
    st.session_state["coverage_reason"] = latest["coverage_reason"]
    st.session_state["pipeline_metrics"] = latest.get("pipeline_metrics", {})
    
def export_investigation(inv_id, title, ext="md"):
    """Generates an export payload for the investigation."""
    messages = get_messages(inv_id)
    content = f"# NEXUS AI Investigation: {title}\n"
    content += f"Exported on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for msg in messages:
        content += f"## User Query: {msg['query']}\n"
        content += f"**Intent:** {msg['query_intent']} | **Coverage:** {msg['coverage']}\n\n"
        content += f"{msg['llm_answer']}\n\n"
        content += "---\n\n"
        
    return content

def group_investigations(investigations):
    groups = {"Pinned": [], "Today": [], "Yesterday": [], "Last 7 Days": [], "Older": []}
    now = time.time()
    
    for inv in investigations:
        if inv["is_pinned"]:
            groups["Pinned"].append(inv)
            continue
            
        diff_days = (now - inv["updated_at"]) / 86400
        
        # Determine group by local calendar days
        local_now = datetime.datetime.fromtimestamp(now)
        local_upd = datetime.datetime.fromtimestamp(inv["updated_at"])
        
        cal_diff = (local_now.date() - local_upd.date()).days
        
        if cal_diff == 0:
            groups["Today"].append(inv)
        elif cal_diff == 1:
            groups["Yesterday"].append(inv)
        elif cal_diff <= 7:
            groups["Last 7 Days"].append(inv)
        else:
            groups["Older"].append(inv)
            
    return groups

def render_sidebar():
    """
    Renders the unified enterprise sidebar with History management.
    """
    with st.sidebar:
        st.title("NEXUS AI")
        st.caption("Enterprise Knowledge Intelligence Platform")
        
        st.button("➕ New Investigation", key="new_investigation_btn", use_container_width=True, type="primary", on_click=start_new_investigation)
        st.button("🧹 Clear Session", key="clear_session_btn", use_container_width=True, on_click=clear_session)
        
        search_query = st.text_input("Search History...", key="search_history_input", placeholder="Filter by title or keyword...", label_visibility="collapsed")
        
        st.divider()
        st.write("### Investigation History")
        
        if search_query.strip():
            investigations = search_investigations(search_query.strip())
        else:
            investigations = get_investigations()
            
        if not investigations:
            st.caption("No investigations found.")
        else:
            groups = group_investigations(investigations)
            
            for group_name, invs in groups.items():
                if not invs: continue
                
                st.caption(f"**{group_name}**")
                
                for inv in invs:
                    title = inv["title"]
                    # Shorten long titles
                    display_title = title if len(title) <= 25 else title[:25] + "..."
                    
                    is_active = st.session_state.get("current_investigation_id") == inv["id"]
                    
                    icon = "📌 " if inv["is_pinned"] else "📄 "
                    with st.expander(f"{icon}{display_title}", expanded=is_active):
                        msgs = get_messages(inv["id"])
                        if msgs:
                            st.caption("**Queries in this session:**")
                            for m in msgs:
                                st.markdown(f"• <span style='font-size:0.85rem; color:#75553B;'>{m['query']}</span>", unsafe_allow_html=True)
                        
                        st.divider()
                        cols = st.columns(2)
                        with cols[0]:
                            if not is_active:
                                st.button("🔄 Load", key=f"load_{inv['id']}", on_click=restore_investigation, args=(inv["id"],), use_container_width=True)
                            else:
                                st.button("✅ Active", key=f"active_{inv['id']}", disabled=True, use_container_width=True)
                        with cols[1]:
                            if not inv["is_pinned"]:
                                if st.button("📌 Pin", key=f"pin_{inv['id']}", use_container_width=True):
                                    update_investigation(inv["id"], is_pinned=True)
                                    st.rerun()
                            else:
                                if st.button("📍 Unpin", key=f"unpin_{inv['id']}", use_container_width=True):
                                    update_investigation(inv["id"], is_pinned=False)
                                    st.rerun()
                                    
                        st.write("**Export & Delete**")
                        dl_cols = st.columns(2)
                        md_export = export_investigation(inv["id"], inv["title"])
                        with dl_cols[0]:
                            st.download_button("📄 .md", data=md_export, file_name=f"{inv['title'].replace(' ', '_')}.md", mime="text/markdown", key=f"export_md_{inv['id']}", use_container_width=True)
                        with dl_cols[1]:
                            st.download_button("📄 .txt", data=md_export, file_name=f"{inv['title'].replace(' ', '_')}.txt", mime="text/plain", key=f"export_txt_{inv['id']}", use_container_width=True)
                            
                        if st.button("🗑️ Delete Investigation", key=f"del_{inv['id']}", use_container_width=True):
                            delete_investigation(inv["id"])
                            if is_active:
                                start_new_investigation()
                            st.rerun()
        
        st.write("")
        st.write("")
        st.write("")
        with st.container(border=True):
            st.page_link("app.py", label="Copilot", icon="💬")
            st.page_link("pages/knowledge_base.py", label="Knowledge Base", icon="📚")
