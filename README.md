# Enterprise Industrial AI Copilot (Nexus Industrial Corp)

## Overview
Industrial AI Copilot is an enterprise-grade AI platform designed to transform fragmented industrial documents into a unified, searchable, and intelligent knowledge system. 
This repository contains the full architecture for implementing a Retrieval-Augmented Generation (RAG) and Enterprise Knowledge Graph (EKG) platform.

## Repository Structure

```text
.
├── backend/            # FastAPI backend services (RAG, Graph, OCR APIs)
├── config/             # Environment variables and logging configurations
├── data/               # Core Enterprise Data Lake
│   ├── archive/        # Archived documents and unutilized images
│   ├── chunks/         # Text chunks for embeddings
│   ├── embeddings/     # Generated embeddings
│   ├── knowledge_graph/# Cypher exports and Neo4j dumps
│   ├── metadata/       # Enterprise Master Tables (Equipment, Documents, Work Orders)
│   ├── processed/      # OCR output and cleaned text
│   ├── raw/            # Immutable source documents (Manuals, Maintenance, Safety)
│   └── vector_db/      # FAISS indices
├── docs/               # Enterprise architecture documents
├── frontend/           # React Dashboard (Future implementation)
├── logs/               # Application logs
├── notebooks/          # Data exploration and RAG evaluation
├── scripts/            # Standalone python scripts for ETL and data ingestion
└── tests/              # Pytest suite
```

## Setup & Installation
1. Copy `config/.env.template` to `config/.env` and insert your API keys.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Boot up the Neo4j Graph Database and Vector DB.
4. Execute `Notebook 1` in `notebooks/` to begin document ingestion.

## MVP Scope (Phase 1)
The current MVP focuses on the **Maintenance Copilot**. The pipeline will ingest OEM Manuals and Synthetic Work Orders to provide troubleshooting and maintenance insights for Nexus Industrial Corp assets.

## License
MIT License
