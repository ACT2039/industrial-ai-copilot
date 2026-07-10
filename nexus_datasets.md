# Nexus Industrial Corp. - AI Platform Datasets Registry

> [!NOTE]
> **Confidentiality Level:** Enterprise Internal
> **Document Purpose:** Defines the core datasets to be ingested into the Nexus Industrial Copilot, outlining their structure, source, and how they empower specific AI modules.

---

## 1. Core Operating Guidelines

### 1.1 Equipment Manuals Dataset
- **Dataset Name:** `Nexus_OEM_Manuals_V1`
- **Purpose:** Foundational knowledge base for equipment specifications, operating limits, and OEM-prescribed troubleshooting steps.
- **Department:** Engineering / Reliability
- **Expected Documents:** Installation Guides, O&M Manuals, Troubleshooting Guides.
- **Source:** External OEM Portals (Simulated via Public Manuals).
- **File Format:** PDF, HTML.
- **AI Module:** Technical Q&A Copilot.
- **Knowledge Graph Usage:** Nodes for Equipment Model, Linked to Troubleshooting Trees.
- **RAG Usage:** High. Primary source for "How do I fix..." queries.
- **OCR Usage:** Medium (Older manuals require OCR).
- **Metadata Fields:** `Equipment ID`, `Manufacturer`, `Revision`, `Language`.
- **Expected Volume:** ~5,000 documents.

### 1.2 Maintenance Logs & Work Orders Dataset
- **Dataset Name:** `Nexus_Maintenance_WO_V1`
- **Purpose:** Historical record of breakdowns, repairs, and parts consumed. Crucial for training the AI to recognize recurring failure patterns.
- **Department:** Maintenance
- **Expected Documents:** Corrective Work Orders, PM Logs, Breakdown Reports.
- **Source:** SAP EAM / CMMS Export (Synthetically generated).
- **File Format:** JSON, CSV, PDF.
- **AI Module:** Predictive Failure Analysis, Diagnostic Copilot.
- **Knowledge Graph Usage:** Links `Equipment` to `Incident`, `Part`, and `Engineer`.
- **RAG Usage:** High. Used to answer "When was the last time the spindle was replaced?"
- **OCR Usage:** Low (Primarily born-digital from CMMS).
- **Metadata Fields:** `Document ID`, `Equipment ID`, `Created Date`, `Status`, `Owner`.
- **Expected Volume:** ~50,000 records/year.

### 1.3 Standard Operating Procedures (SOP) Dataset
- **Dataset Name:** `Nexus_EHS_SOP_V1`
- **Purpose:** Dictates the safe and standard way to execute tasks, including LOTO (Lockout/Tagout) and confined space entry.
- **Department:** Safety (EHS)
- **Expected Documents:** SOPs, JHAs (Job Hazard Analyses), Safety Policies.
- **Source:** SharePoint Document Control System (Synthetically generated).
- **File Format:** PDF, DOCX.
- **AI Module:** Safety Compliance Copilot.
- **Knowledge Graph Usage:** Links `SOP` to `Equipment` and `Department`.
- **RAG Usage:** High. Used to generate step-by-step guidance.
- **OCR Usage:** Low.
- **Metadata Fields:** `Document ID`, `Department`, `Revision`, `Updated Date`.
- **Expected Volume:** ~1,500 documents.

### 1.4 Quality & Inspection Dataset
- **Dataset Name:** `Nexus_Quality_Assurance_V1`
- **Purpose:** Tracks manufacturing defects and dimensional out-of-tolerance events.
- **Department:** Quality
- **Expected Documents:** NCRs (Non-Conformance Reports), Audit Reports, CMM Inspection Logs.
- **Source:** Quality Management System (QMS).
- **File Format:** PDF, CSV, Excel.
- **AI Module:** Quality Root Cause Copilot.
- **Knowledge Graph Usage:** Links `Quality_Report` to `Equipment` and `Reliability_Report`.
- **RAG Usage:** Medium. Used to correlate maintenance events with quality drops.
- **OCR Usage:** Medium (Handwritten inspection forms).
- **Metadata Fields:** `Document ID`, `Plant`, `Area`, `Status`.
- **Expected Volume:** ~10,000 records/year.

### 1.5 Incident & Safety Dataset
- **Dataset Name:** `Nexus_Incident_Logs_V1`
- **Purpose:** Documents safety near-misses, environmental spills, and injuries.
- **Department:** Safety (EHS)
- **Expected Documents:** Incident Reports, OSHA Logs.
- **Source:** EHS Management Portal.
- **File Format:** PDF, JSON.
- **AI Module:** Risk Mitigation AI.
- **Knowledge Graph Usage:** Links `Incident` to `Equipment`, `SOP` (violations), and `Engineer`.
- **RAG Usage:** Medium.
- **OCR Usage:** Low.
- **Metadata Fields:** `Document ID`, `Created Date`, `Confidentiality` (Highly Restricted).
- **Expected Volume:** ~500 records/year.

### 1.6 Engineering & Drawings Dataset
- **Dataset Name:** `Nexus_Engineering_CAD_V1`
- **Purpose:** Visual and schematic representation of the plant and assets.
- **Department:** Engineering
- **Expected Documents:** P&IDs, CAD Drawings, Equipment Specifications.
- **Source:** PLM (Product Lifecycle Management) Vault.
- **File Format:** PDF, DXF, DWG.
- **AI Module:** Visual Diagnostic Copilot.
- **Knowledge Graph Usage:** Node for `Engineering_Drawing` linked to `Equipment`.
- **RAG Usage:** Low for text, High for Vision-Language Models (VLM).
- **OCR Usage:** High (Extracting tags and labels from P&IDs).
- **Metadata Fields:** `Equipment ID`, `Revision`, `Tags`.
- **Expected Volume:** ~20,000 drawings.

### 1.7 Supply Chain & Inventory Dataset
- **Dataset Name:** `Nexus_Supply_Chain_V1`
- **Purpose:** Tracks availability of spare parts and vendor performance.
- **Department:** Procurement / Inventory
- **Expected Documents:** Purchase Orders, Vendor Contracts, Spare Parts Ledgers.
- **Source:** ERP System (SAP/Oracle).
- **File Format:** CSV, PDF.
- **AI Module:** Supply Chain Optimization AI.
- **Knowledge Graph Usage:** Links `Inventory_Part` to `Supplier` and `Maintenance_Log`.
- **RAG Usage:** Medium. Used to answer "Do we have part BRG-992 in stock and who supplies it?"
- **OCR Usage:** Medium (Scanned vendor invoices).
- **Metadata Fields:** `Document ID`, `Manufacturer`, `Created Date`.
- **Expected Volume:** ~100,000 records/year.
