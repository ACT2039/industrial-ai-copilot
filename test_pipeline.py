import json
import os
import networkx as nx
from services.retrieval_service import load_faiss_index, load_metadata_and_chunks
from services.graph_service import load_knowledge_graph
from components.chat_panel import execute_pipeline
import streamlit as st

# Setup Mock Session State
class MockSessionState(dict):
    def __getattr__(self, key):
        return self.get(key, None)
    def __setattr__(self, key, value):
        self[key] = value

st.session_state = MockSessionState()
st.session_state["investigation_history"] = []
st.session_state["current_investigation_id"] = None
st.session_state["is_processing"] = False
st.session_state["general_ai_mode"] = False

# Mocks for Streamlit functions
class MockStatus:
    def __init__(self, *args, **kwargs): pass
    def __enter__(self): return self
    def __exit__(self, *args, **kwargs): pass
    def update(self, *args, **kwargs): pass

class MockContext:
    def __init__(self, *args, **kwargs): pass
    def __enter__(self): return self
    def __exit__(self, *args, **kwargs): pass
    def caption(self, *args, **kwargs): pass
    def write(self, *args, **kwargs): pass
    def markdown(self, *args, **kwargs): pass

st.status = MockStatus
st.chat_message = MockContext
st.caption = lambda *args, **kwargs: None
st.write = lambda *args, **kwargs: None
st.error = lambda *args, **kwargs: None
st.warning = lambda *args, **kwargs: None
st.success = lambda *args, **kwargs: None
st.columns = lambda n, **kwargs: [MockContext()] * n
st.markdown = lambda *args, **kwargs: None
st.divider = lambda *args, **kwargs: None
st.button = lambda *args, **kwargs: None

print("Loading Resources...")
load_faiss_index()
load_metadata_and_chunks()
load_knowledge_graph()

print("Executing Pipeline...")
try:
    execute_pipeline("What is the maintenance procedure for the compressor?")
except Exception as e:
    import traceback
    traceback.print_exc()

metrics = st.session_state.get("pipeline_metrics", {})
print("\n--- EXTRACTED PIPELINE METRICS ---")
for k, v in metrics.items():
    print(f"{k}: {v} ({type(v).__name__})")

if not metrics:
    print("FAILED: Metrics are empty!")
else:
    print("\nVerifying non-zero values...")
    assert metrics["retrieved_chunks"] > 0, "No chunks retrieved!"
    assert metrics["prompt_length"] > 0, "Prompt is empty!"
    assert metrics["context_length"] > 0, "Context is empty!"
    assert metrics["total_tokens"] > 0, "Tokens are 0!"
    print("ALL METRICS VERIFIED SUCCESSFULLY.")
