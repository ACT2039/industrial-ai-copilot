# Knowledge Graph Relationship Matrix & Cypher Readiness

## Node Types
- `Equipment`: Represents physical assets (e.g., CNC-601).
- `WorkOrder`: Represents a maintenance action (e.g., WO-2026-001).
- `Part`: Represents a physical spare part (e.g., BRG-992-SKF).
- `Document`: Represents a manual or SOP (e.g., ENG-MAN-CNC601-SIEMENS-001.pdf).
- `Engineer`: Represents personnel (e.g., John Doe).

## Relationship Matrix

| Source Node | Relationship Type | Target Node | Description |
| :--- | :--- | :--- | :--- |
| WorkOrder | `REFERENCES` | Equipment | Links the maintenance log to the asset it was performed on. |
| WorkOrder | `PERFORMED_BY` | Engineer | Links the work order to the technician who executed it. |
| WorkOrder | `CONSUMES` | Part | Links the work order to the spare parts used during repair. |
| WorkOrder | `FOLLOWS` | Document | Links the work order to the Manual or SOP used as a reference. |
| Document | `COVERS` | Equipment | Links an OEM Manual to the Equipment it describes. |
| Part | `COMPATIBLE_WITH` | Equipment | Links a spare part directly to the equipment it fits. |

## Cypher Base Queries (For Implementation)

**1. Create Equipment Node**
```cypher
MERGE (e:Equipment {id: "CNC-601"})
SET e.name = "5-Axis Machining Center A", e.mfg = "Siemens", e.criticality = "High"
```

**2. Create Work Order and Link to Equipment & Parts**
```cypher
MERGE (w:WorkOrder {id: "WO-2026-001"})
SET w.issue = "Spindle vibration high", w.date = "2026-07-01"

MERGE (e:Equipment {id: "CNC-601"})
MERGE (w)-[:REFERENCES]->(e)

MERGE (p:Part {id: "BRG-992-SKF"})
MERGE (w)-[:CONSUMES]->(p)

MERGE (d:Document {id: "ENG-MAN-CNC601-SIEMENS-001.pdf"})
MERGE (w)-[:FOLLOWS]->(d)
```

**3. GraphRAG Retrieval Query (Context for LLM)**
```cypher
MATCH (e:Equipment {id: $equipment_id})<-[:REFERENCES]-(w:WorkOrder)-[:CONSUMES]->(p:Part)
OPTIONAL MATCH (w)-[:FOLLOWS]->(d:Document)
RETURN w.issue AS Issue, w.resolution AS Resolution, p.id AS Part_Replaced, d.id AS Manual_Used
ORDER BY w.date DESC LIMIT 5
```
