# CELL 0
# ==========================================================
# Notebook 8
# Industrial Knowledge Graph
# ==========================================================

import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from pathlib import Path
from datetime import datetime

# CELL 1
# ==========================================================
# Universal Notebook Setup
# Compatible with VS Code • GitHub • Local Development
# ==========================================================

import sys
from pathlib import Path

# ----------------------------------------------------------
# Step 1: Automatically locate PROJECT_ROOT
# ----------------------------------------------------------
_current_dir = Path.cwd().resolve()
PROJECT_ROOT = None

# Search upwards (max 5 levels) for src/core/config.py
for _ in range(5):
    if (_current_dir / "src" / "core" / "config.py").is_file():
        PROJECT_ROOT = _current_dir
        break
    _current_dir = _current_dir.parent

if PROJECT_ROOT is None:
    raise FileNotFoundError(
        "❌ Could not automatically determine PROJECT_ROOT.\n
"
        "Please make sure the notebook is opened from inside the project."
    )

# ----------------------------------------------------------
# Step 2: Add PROJECT_ROOT to Python path (if needed)
# ----------------------------------------------------------
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ----------------------------------------------------------
# Step 3: Import centralized configuration
# ----------------------------------------------------------
from src.core.config import (
    PROJECT_ROOT as CONFIG_ROOT,
    DATA_DIR,
    RAW_DIR,
    PROCESSED_DIR,
    CHUNK_DIR,
    EMBEDDING_DIR,
    VECTOR_DB_DIR,
    KG_DIR,
    INVENTORY_DIR,
    LOG_DIR,
)

# ----------------------------------------------------------
# Step 4: Verify PROJECT_ROOT consistency
# ----------------------------------------------------------
if CONFIG_ROOT != PROJECT_ROOT:
    print("⚠ WARNING: Notebook PROJECT_ROOT differs from config.py PROJECT_ROOT")
    print(f"Notebook : {PROJECT_ROOT}")
    print(f"Config   : {CONFIG_ROOT}")

# Use the centralized PROJECT_ROOT from config.py
PROJECT_ROOT = CONFIG_ROOT

# ----------------------------------------------------------
# Step 5: Verify required directories exist
# ----------------------------------------------------------
required_dirs = [
    DATA_DIR,
    RAW_DIR,
    PROCESSED_DIR,
    CHUNK_DIR,
    EMBEDDING_DIR,
    VECTOR_DB_DIR,
    KG_DIR,
    INVENTORY_DIR,
    LOG_DIR,
]

missing_dirs = [d for d in required_dirs if not d.exists()]

if missing_dirs:
    print("\n
❌ Missing Directories:")
    for d in missing_dirs:
        print(f"   - {d}")
    raise FileNotFoundError("One or more required directories are missing.")

# ----------------------------------------------------------
# Step 6: Environment Verification
# ----------------------------------------------------------
print("=" * 65)
print("PROJECT SETUP VERIFICATION SUMMARY")
print("=" * 65)
print(f"PROJECT_ROOT      : {PROJECT_ROOT}")
print(f"DATA_DIR          : {DATA_DIR}")
print(f"RAW_DIR           : {RAW_DIR}")
print(f"PROCESSED_DIR     : {PROCESSED_DIR}")
print(f"CHUNK_DIR         : {CHUNK_DIR}")
print(f"EMBEDDING_DIR     : {EMBEDDING_DIR}")
print(f"VECTOR_DB_DIR     : {VECTOR_DB_DIR}")
print(f"KG_DIR            : {KG_DIR}")
print(f"INVENTORY_DIR     : {INVENTORY_DIR}")
print(f"LOG_DIR           : {LOG_DIR}")
print("-" * 65)
print("✅ Status          : SUCCESS")
print("=" * 65)


# CELL 2
chunks = pd.read_parquet(
    CHUNK_DIR / "chunks.parquet"
)

print("Chunks:", len(chunks))

display(chunks.head())

# CELL 3
chunk_meta = pd.read_parquet(
    CHUNK_DIR / "chunk_metadata.parquet"
)

display(chunk_meta.head())

# CELL 4
import glob

rag_files = glob.glob(
    str(RAG_DIR / "*.json")
)

print("RAG files:", len(rag_files))

# CELL 5
kg = nx.Graph()

print("Knowledge Graph Initialized")

# CELL 6
from openai import OpenAI
from google.colab import userdata
import json

# CELL 7
client = OpenAI(
    api_key=userdata.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# CELL 8
MODEL = "deepseek/deepseek-chat-v3-0324"

# CELL 9
ENTITY_PROMPT = """
You are an information extraction engine.

You MUST return ONLY valid JSON.

Do not explain.

Do not add markdown.

Do not use ```json.

Do not add any text before or after JSON.

Output must exactly follow this schema:

{
  "entities":[
      {
          "name":"...",
          "type":"Equipment"
      }
  ],
  "relationships":[
      {
          "source":"...",
          "target":"...",
          "relation":"..."
      }
  ]
}

If no entities are found:

{
  "entities":[],
  "relationships":[]
}
"""

# CELL 10
# ==========================================================
# Local Industrial Entity Extraction
# ==========================================================

import re

# Safety-related keywords
SAFETY = {
    "danger","warning","caution","notice","ppe","helmet",
    "gloves","goggles","ear protection","eye protection",
    "respirator","flammable","hot","hazard","electric",
    "voltage","high voltage","lockout","tagout",
    "emergency","fire","explosion","toxic","chemical"
}

# Maintenance-related keywords
MAINTENANCE = {
    "inspect","replace","clean","lubricate","tighten",
    "repair","maintenance","service","adjust","remove",
    "install","check","calibrate","grease","oil"
}

# Equipment keywords
EQUIPMENT = {
    "pump","motor","compressor","gearbox","bearing",
    "valve","filter","sensor","switch","fan",
    "conveyor","cylinder","belt","pipe","tank",
    "engine","machine","generator","transformer",
    "battery","hydraulic","pneumatic"
}


def extract_entities(text):

    text = str(text).lower()

    entities = []

    words = re.findall(r"[a-zA-Z0-9\-]+", text)

    # Safety
    for keyword in SAFETY:
        if keyword in text:
            entities.append({
                "name": keyword.title(),
                "type": "Safety"
            })

    # Maintenance
    for keyword in MAINTENANCE:
        if keyword in text:
            entities.append({
                "name": keyword.title(),
                "type": "Maintenance"
            })

    # Equipment
    for keyword in EQUIPMENT:
        if keyword in text:
            entities.append({
                "name": keyword.title(),
                "type": "Equipment"
            })

    # Equipment Codes
    for code in re.findall(r"[A-Z]{2,5}-?\d{2,6}", text.upper()):

        entities.append({
            "name": code,
            "type": "Equipment_Code"
        })

    # Remove duplicates

    unique = {}

    for e in entities:
        unique[e["name"]] = e

    return list(unique.values())

# CELL 11
# ==========================================================
# Create Multi-Type Knowledge Graph
# ==========================================================

kg = nx.Graph()

print("Knowledge Graph Initialized")

# CELL 12
# ==========================================================
# Add Node
# ==========================================================

def add_node(node_id, node_type, **attributes):

    if not kg.has_node(node_id):

        kg.add_node(

            node_id,

            node_type=node_type,

            **attributes

        )

# CELL 13
# ==========================================================
# Add Edge
# ==========================================================

def add_edge(source, target, relation):

    if not kg.has_edge(source, target):

        kg.add_edge(

            source,

            target,

            relation=relation

        )

# CELL 14
# ==========================================================
# Document Nodes
# ==========================================================

for _, row in chunks.iterrows():

    add_node(

        row["Document_ID"],

        "Document",

        file=row["File_Name"]

    )

print("Document Nodes Added")

# CELL 15
# ==========================================================
# Chunk Nodes
# ==========================================================

for _, row in chunks.iterrows():

    add_node(

        row["Chunk_ID"],

        "Chunk",

        page=row["Page_Number"],

        chunk=row["Chunk_Number"]

    )

    add_edge(

        row["Document_ID"],

        row["Chunk_ID"],

        "contains"

    )

print("Chunk Nodes Added")

# CELL 16
# ==========================================================
# Local Knowledge Graph Construction
# ==========================================================

from itertools import combinations
from tqdm import tqdm

print("="*60)
print("Building Knowledge Graph (Local NLP)")
print("="*60)

entity_count = 0

for _, row in tqdm(chunks.iterrows(), total=len(chunks)):

    chunk_id = row["Chunk_ID"]
    text = row["Chunk_Text"]

    entities = extract_entities(text)

    entity_names = []

    for entity in entities:

        name = entity["name"]
        node_type = entity["type"]

        add_node(
            name,
            node_type
        )

        add_edge(
            chunk_id,
            name,
            "mentions"
        )

        entity_names.append(name)

        entity_count += 1

    # Create entity co-occurrence edges
    for e1, e2 in combinations(sorted(set(entity_names)), 2):

        add_edge(
            e1,
            e2,
            "co_occurs"
        )

print("="*60)
print("Knowledge Graph Completed")
print("="*60)

print(f"Total Nodes : {kg.number_of_nodes():,}")
print(f"Total Edges : {kg.number_of_edges():,}")
print(f"Entities    : {entity_count:,}")

# CELL 17
# ==========================================================
# Basic Graph Statistics
# ==========================================================

print("=" * 60)
print("KNOWLEDGE GRAPH STATISTICS")
print("=" * 60)

print(f"Nodes               : {kg.number_of_nodes():,}")
print(f"Edges               : {kg.number_of_edges():,}")
print(f"Density             : {nx.density(kg):.6f}")
print(f"Connected Components: {nx.number_connected_components(kg)}")
print(f"Average Degree      : {sum(dict(kg.degree()).values()) / kg.number_of_nodes():.2f}")

print("=" * 60)

# CELL 18
# ==========================================================
# Degree Centrality
# ==========================================================

degree = nx.degree_centrality(kg)

degree_df = (
    pd.DataFrame(
        degree.items(),
        columns=["Node", "Degree_Centrality"]
    )
    .sort_values(
        "Degree_Centrality",
        ascending=False
    )
)

degree_df.head(20)

# CELL 19
# ==========================================================
# Betweenness (Sampled)
# ==========================================================

sample_nodes = list(kg.nodes())[:5000]

sample_graph = kg.subgraph(sample_nodes)

betweenness = nx.betweenness_centrality(sample_graph)

betweenness_df = (
    pd.DataFrame(
        betweenness.items(),
        columns=["Node", "Betweenness"]
    )
    .sort_values(
        "Betweenness",
        ascending=False
    )
)

betweenness_df.head(20)

# CELL 20
# ==========================================================
# Closeness
# ==========================================================

closeness = nx.closeness_centrality(sample_graph)

closeness_df = (
    pd.DataFrame(
        closeness.items(),
        columns=["Node", "Closeness"]
    )
    .sort_values(
        "Closeness",
        ascending=False
    )
)

closeness_df.head(20)

# CELL 21
# ==========================================================
# Equipment Ranking
# ==========================================================

equipment_nodes = [

    node

    for node, attr in kg.nodes(data=True)

    if attr.get("node_type") == "Equipment"

]

equipment_stats = []

for node in equipment_nodes:

    equipment_stats.append({

        "Equipment": node,

        "Connections": kg.degree(node)

    })

equipment_df = pd.DataFrame(equipment_stats)

equipment_df.sort_values(

    "Connections",

    ascending=False,

    inplace=True

)

equipment_df.head(20)

# CELL 22
maintenance_nodes = [

    node

    for node, attr in kg.nodes(data=True)

    if attr.get("node_type") == "Maintenance"

]

maintenance_stats = []

for node in maintenance_nodes:

    maintenance_stats.append({

        "Action": node,

        "Connections": kg.degree(node)

    })

maintenance_df = pd.DataFrame(maintenance_stats)

maintenance_df.sort_values(

    "Connections",

    ascending=False,

    inplace=True

)

maintenance_df.head(20)

# CELL 23
safety_nodes = [

    node

    for node, attr in kg.nodes(data=True)

    if attr.get("node_type") == "Safety"

]

safety_stats = []

for node in safety_nodes:

    safety_stats.append({

        "Safety": node,

        "Connections": kg.degree(node)

    })

safety_df = pd.DataFrame(safety_stats)

safety_df.sort_values(

    "Connections",

    ascending=False,

    inplace=True

)

safety_df.head(20)

# CELL 24
components = list(nx.connected_components(kg))

print("Connected Components:", len(components))

largest = max(components, key=len)

print("Largest Component Size:", len(largest))

# CELL 25
# ==========================================================
# Export Statistics
# ==========================================================

stats = {

    "Nodes": kg.number_of_nodes(),

    "Edges": kg.number_of_edges(),

    "Density": nx.density(kg),

    "Connected_Components": len(components),

    "Largest_Component": len(largest)

}

with open(

    KG_DIR / "knowledge_graph_statistics.json",

    "w"

) as f:

    json.dump(

        stats,

        f,

        indent=4

    )

print("Statistics Saved")

# CELL 26
# ==========================================================
# Save Knowledge Graph
# ==========================================================

import pickle
import os

os.makedirs(KG_DIR, exist_ok=True)

kg_path = os.path.join(KG_DIR, "knowledge_graph.gpickle")

with open(kg_path, "wb") as f:
    pickle.dump(kg, f)

print("="*60)
print("Knowledge Graph Saved Successfully")
print("="*60)

print(f"Nodes : {kg.number_of_nodes():,}")
print(f"Edges : {kg.number_of_edges():,}")

print(f"\nSaved to:\n{kg_path}")

