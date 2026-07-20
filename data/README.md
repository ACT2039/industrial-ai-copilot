# Enterprise Dataset Architecture

Welcome to the `data/` directory of the Industrial AI Copilot.

## Why the Complete Dataset is Not Included
To keep this repository lightweight, professional, and easily clobable, the **complete raw dataset** (>500MB of PDFs and Images) is **not** included in the version history. 

Committing hundreds of heavy OEM manuals to GitHub is an anti-pattern in Enterprise AI engineering. It bloats the `.git` directory and increases clone times drastically. 

## Dataset Structure
- `data/metadata/`: **(Tracked)** Contains the synthetic enterprise data (CSV files) detailing equipment masters, work orders, and relationships.
- `data/raw/`: **(Ignored)** The landing zone for all raw PDFs and Images.
- `samples/`: **(Tracked)** A lightweight directory containing ~10 representative files for immediate testing.

## How to Recreate the Dataset
If you want to run the full pipeline on your local machine:
1. Refer to `docs/dataset_sources.md` for the list of public OEM websites.
2. Download the manuals you need.
3. Place the PDF files inside `data/raw/manuals/<mfg>/`.
4. Follow the step-by-step instructions in `docs/reproduce_dataset.md` to ensure file naming conventions match our `metadata.csv`.
5. Run `Notebook 1` (`notebooks/01_document_discovery.ipynb`). The pipeline will automatically scan `data/raw/` and integrate your downloaded files into the RAG ingestion stream!
