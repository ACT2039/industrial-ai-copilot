# Enterprise Industrial AI Copilot (Nexus Industrial Corp)

## Overview
Industrial AI Copilot is an enterprise-grade AI platform designed to transform fragmented industrial documents into a unified, searchable, and intelligent knowledge system. 
This repository contains the full architecture for implementing a Retrieval-Augmented Generation (RAG) and Enterprise Knowledge Graph (EKG) platform.

## Repository Philosophy
This project strictly follows open-source and enterprise AI software engineering best practices. We separate **Code** from **Data**. To prevent repository bloat and ensure fast cloning, heavy binary datasets (large PDFs, OCR images) are intentionally `.gitignore`d. Instead, we rely on lightweight synthetic CSVs for architecture validation and provide a small sample dataset for immediate testing.

## Repository Structure

```text
.
├── backend/            # FastAPI backend services (RAG, Graph, OCR APIs)
├── config/             # Environment variables and logging configurations
├── data/               # Core Enterprise Data Lake
│   ├── archive/        # Archived documents and unutilized images
│   ├── metadata/       # Tracked: Enterprise Master Tables (Equipment, Documents, Work Orders)
│   ├── raw/            # Ignored: Immutable source documents (Manuals, Maintenance, Safety)
│   └── ...             # Ignored: chunks/, embeddings/, vector_db/, processed/
├── docs/               # Enterprise architecture and dataset documentation
├── frontend/           # React Dashboard (Future implementation)
├── logs/               # Application logs
├── notebooks/          # Data exploration and RAG evaluation
├── samples/            # Tracked: Lightweight 10-file sample dataset for demo purposes
├── scripts/            # Standalone python scripts for ETL and data ingestion
└── tests/              # Pytest suite
```

## Dataset Strategy

### The Enterprise Dataset (Tracked)
All structural data is tracked in Git. You will find the complete synthetic enterprise environment inside `data/metadata/`:
- `equipment_master.csv`
- `metadata.csv`
- `work_orders.csv`
- `maintenance_logs.csv`
- `spare_parts.csv`

### The Sample Dataset (Tracked)
Located in `samples/`, this folder contains a representative subset of PDFs and Images (Siemens manual, ABB manual, OSHA SOP, and a few labels). It is designed to let recruiters and judges test the document ingestion pipeline without heavy downloads.

## Reproducing Results & Public Data Sources
If you wish to run the AI Copilot on the complete, hundreds-of-megabytes dataset, you must reconstruct it locally. 
- Please see **[`docs/dataset_sources.md`](docs/dataset_sources.md)** for links to the public OEM manuals (Siemens, ABB, Atlas Copco).
- Please see **[`docs/reproduce_dataset.md`](docs/reproduce_dataset.md)** for exact instructions on where to place the downloaded files and how to name them.

## Setup & Installation
1. Copy `config/.env.template` to `config/.env` and insert your API keys.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Reconstruct the complete `data/raw/` dataset via our documentation.
4. Execute `Notebook 1` in `notebooks/` to begin document discovery and pipeline ingestion.

## MVP Scope (Phase 1)
The current MVP focuses on the **Maintenance Copilot**. The pipeline will ingest OEM Manuals and Synthetic Work Orders to provide troubleshooting and maintenance insights for Nexus Industrial Corp assets.

## License
MIT License
