# Public Data Sources

The Industrial AI Copilot processes complex technical documentation. To build the initial `data/raw/` dataset, we utilized publicly available manuals and safety regulations from leading industrial manufacturers and regulatory bodies.

| Organization | Website | Document Types | Purpose | Folder |
| :--- | :--- | :--- | :--- | :--- |
| **Siemens** | [siemens.com/support](https://support.industry.siemens.com/) | CNC Operating Manuals | Machining Center RAG | `data/raw/manuals/siemens/` |
| **ABB** | [abb.com/robotics](https://new.abb.com/products/robotics) | Industrial Robot & Pump Manuals | Robotics & Fluid RAG | `data/raw/manuals/abb/` |
| **Schneider Electric** | [se.com/docs](https://www.se.com/ww/en/download/) | Motor Drive & PLC Manuals | Electrical Systems RAG | `data/raw/manuals/schneider/` |
| **Atlas Copco** | [atlascopco.com](https://www.atlascopco.com/) | Compressor Service Manuals | Utilities RAG | `data/raw/manuals/atlas_copco/` |
| **Grundfos** | [grundfos.com](https://www.grundfos.com/) | Centrifugal Pump Datasheets | Fluid Systems RAG | `data/raw/manuals/grundfos/` |
| **OSHA** | [osha.gov/publications](https://www.osha.gov/publications) | Safety Posters & Standards | Safety & Compliance RAG | `data/raw/safety_and_regulations/` |

> [!TIP]
> You are not required to download the exact same manuals we used. You can download any PDF from these sources, place them in `data/raw/`, and register them in `metadata.csv` to expand the AI's knowledge base!
