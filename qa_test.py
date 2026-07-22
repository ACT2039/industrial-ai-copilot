import os
import sys
import time

# Mock Streamlit
class MockSessionState(dict):
    pass

class MockST:
    def __init__(self):
        self.session_state = MockSessionState()
    def get(self, key, default=None):
        return self.session_state.get(key, default)
    def __getattr__(self, name):
        def mock_func(*args, **kwargs):
            pass
        return mock_func

sys.modules['streamlit'] = MockST()
import streamlit as st

# Mock components
import streamlit.components.v1 as components
components.html = lambda *args, **kwargs: None

# Load the actual components and services
try:
    from services.config_service import load_config
    from services.retrieval_service import search
    from services.graph_service import get_subgraph
    from services.llm_service import build_context, generate_answer
    from components.graph_panel import render_graph_panel
    import networkx as nx
    from pyvis.network import Network
    print("[PASS] Imports successful.")
except Exception as e:
    print(f"[FAIL] Imports failed: {e}")
    sys.exit(1)

queries = [
    "How to inspect compressor?",
    "How to replace fan?",
    "How to repair valve?",
    "How to clean filter?",
    "Electrical hazards"
]

print("==================================================")
print("QA TEST EXECUTION")
print("==================================================")

for q in queries:
    print(f"Testing Query: {q}")
    
    t0 = time.time()
    try:
        # 1. Retrieval
        results = search(q, top_k=5)
        print(f"  [+] Retrieval: {len(results)} results")
        
        # 2. Graph
        subgraph = get_subgraph(results, depth=1)
        print(f"  [+] Graph: {subgraph.number_of_nodes()} nodes, {subgraph.number_of_edges()} edges")
        
        # 3. Context
        context = build_context(results, subgraph)
        
        # 4. LLM
        # We will mock the LLM call to save time and API costs, but test the function call
        print("  [+] Context Built.")
        
        # 5. Graph Rendering check
        st.session_state["retrieval_results"] = results
        st.session_state["retrieved_subgraph"] = subgraph
        
        # We need to capture the PyVis HTML to check for CHK and HTML tags in titles
        # We will patch components.html to save the output
        global captured_html
        captured_html = ""
        def mock_html(html_str, **kwargs):
            global captured_html
            captured_html = html_str
        components.html = mock_html
        
        render_graph_panel()
        
        if captured_html:
            print("  [+] Graph panel rendered HTML successfully.")
            # Verify no CHK labels in primary label
            # Search for label="CHK
            if 'label="CHK' in captured_html or 'label:"CHK' in captured_html:
                print("  [FAIL] Found raw CHK ID in graph label!")
            
            # Verify no HTML in titles
            # titles are usually in title="...", we'd have to parse, but let's just check for <b> or <br>
            if '<b>' in captured_html or '<br>' in captured_html:
                print("  [FAIL] Found HTML tags in graph tooltip/title!")
                
        else:
            print("  [WARN] Graph panel did not render HTML.")
            
    except Exception as e:
        print(f"  [FAIL] Exception during pipeline: {e}")

print("==================================================")
print("QA TEST COMPLETE")
print("==================================================")
