# Reproducing the Complete Dataset

To maintain a professional GitHub repository, we do not commit large binary blobs. However, total reproducibility is a core tenet of this project. 

Follow these steps to reconstruct the complete enterprise dataset on your local machine.

## Step 1: Recreate the Directory Structure
First, ensure that the ignored directories exist locally:
```bash
mkdir -p data/raw/manuals/siemens
mkdir -p data/raw/manuals/abb
mkdir -p data/raw/manuals/schneider
mkdir -p data/raw/manuals/atlas_copco
mkdir -p data/raw/safety_and_regulations
mkdir -p data/raw/images/equipment_labels
mkdir -p data/raw/images/inspection_forms
mkdir -p data/raw/images/gauges
```

## Step 2: Download the Source Files
Refer to `docs/dataset_sources.md` and download technical manuals from the respective manufacturers. 

## Step 3: Enforce Enterprise Naming Conventions
The AI Copilot relies on structured filenames to link unstructured text to the Knowledge Graph. Rename your downloaded files to match the `Document_Name` column in `data/metadata/metadata.csv`.

**Naming Format:**
`[Department]-[DocType]-[EquipmentID]-[Manufacturer]-[Sequence].pdf`

**Examples:**
- `ENG-MAN-CNC601-SIEMENS-001.pdf`
- `ENG-MAN-P101-ABB-001.pdf`
- `EHS-SOP-LOTO-001.pdf`

Move the renamed PDFs into their respective `data/raw/manuals/` subdirectories.

## Step 4: Add Sample Images for OCR Testing
If you wish to test the Vision-Language pipelines:
1. Search public image repositories for industrial labels, analog gauges, or handwritten inspection checklists.
2. Save them as `.jpg` or `.png` inside `data/raw/images/`.
3. They do not require strict naming conventions, as the OCR pipeline iterates blindly through the image directory.

## Step 5: Run Discovery
Once the files are placed in `data/raw/`, run Notebook 1:
```bash
jupyter notebook notebooks/01_document_discovery.ipynb
```
The pipeline will securely hash and inventory your locally reconstructed dataset!
