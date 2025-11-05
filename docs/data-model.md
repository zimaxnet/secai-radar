# SecAI Radar — Data Model

> Defines the Bronze/Silver schemas and data layer patterns for cloud security assessment evidence.

---

## Data Layer Architecture

The data model follows a **Bronze → Silver → Gold/RAG** pattern:

1. **Bronze**: Raw JSON from discovery/collectors (timestamped, immutable)
2. **Silver**: Normalized records with resource, domain, control, status
3. **Gold/RAG**: Text chunks of silver data, embedded and searchable

---

## Bronze Layer (Raw Evidence)

### Purpose
Store raw, unprocessed evidence from cloud discovery and collectors. This layer is **immutable** and **timestamped** for audit and lineage tracking.

### Schema

```json
{
  "id": "bronze-{timestamp}-{uuid}",
  "timestamp": "2025-01-15T10:30:00Z",
  "source": "collector-{name}",
  "tenant_id": "tenant-{identifier}",
  "subscription_id": "subscription-{identifier}",
  "resource_type": "storage_account|vm|nsg|...",
  "resource_id": "resource-{identifier}",
  "raw_data": {
    // Raw JSON payload from collector
    // Structure varies by collector and resource type
  },
  "metadata": {
    "collector_version": "1.0.0",
    "collection_method": "api|cli|sdk",
    "tags": ["network", "security"]
  }
}
```

### Storage
- **Format**: JSON files in blob storage or NoSQL database
- **Partitioning**: By timestamp (e.g., `year/month/day/`) or tenant_id
- **Retention**: Configurable per tenant (default: 90 days)

### Characteristics
- Immutable (append-only)
- Preserves original structure and context
- Supports audit trail and data lineage
- No normalization or transformation

---

## Silver Layer (Normalized Evidence)

### Purpose
Normalize bronze data into a common data model with consistent structure across all resource types. Maps evidence to **controls** and **domains**.

### Schema

```json
{
  "id": "silver-{tenant_id}-{domain_code}-{control_id}",
  "timestamp": "2025-01-15T10:30:00Z",
  "tenant_id": "tenant-{identifier}",
  "subscription_id": "subscription-{identifier}",
  "resource_type": "storage_account|vm|nsg|...",
  "resource_id": "resource-{identifier}",
  "domain_code": "NET|IDM|LOG|SEC|...",
  "control_id": "SEC-NET-0007|SEC-IDM-0001|...",
  "control_title": "Network Security Group Rules",
  "status": "compliant|non_compliant|not_applicable|unknown",
  "evidence": {
    "raw_data_ref": "bronze-{id}",
    "normalized_fields": {
      // Extracted and normalized fields
      "nsg_rules": [...],
      "allowed_ports": [...],
      "source_addresses": [...]
    },
    "evidence_links": ["blob://evidence/file1.json"],
    "screenshots": ["blob://screenshots/nsg-rules.png"]
  },
  "scoring": {
    "coverage_score": 0.85,
    "config_score": 0.90,
    "composite_score": 0.875
  },
  "normalization_metadata": {
    "normalizer_version": "1.0.0",
    "normalized_at": "2025-01-15T10:35:00Z",
    "confidence": 0.95
  }
}
```

### Key Fields

- **`domain_code`**: Security domain (e.g., `NET` for Network, `IDM` for Identity, `LOG` for Logging)
- **`control_id`**: Unique control identifier (e.g., `SEC-NET-0007`)
- **`status`**: Compliance status based on evidence analysis
- **`evidence`**: Links to bronze data and normalized fields
- **`scoring`**: Coverage and configuration quality scores

### Storage
- **Format**: Structured records in table storage or database
- **Partitioning**: By `tenant_id` and `domain_code`
- **Indexing**: On `control_id`, `status`, `resource_type`

### Normalization Rules
- Extract common fields from bronze data
- Map resource configurations to control requirements
- Standardize status values across all resource types
- Preserve links to original bronze data

---

## Gold/RAG Layer (Embedded Searchable)

### Purpose
Convert silver data into text chunks suitable for AI/RAG retrieval. Embed chunks for semantic search and context retrieval.

### Schema

```json
{
  "chunk_id": "gold-{tenant_id}-{domain_code}-{control_id}-{chunk_index}",
  "tenant_id": "tenant-{identifier}",
  "domain_code": "NET|IDM|LOG|...",
  "control_id": "SEC-NET-0007",
  "chunk_index": 0,
  "text_content": "Network Security Group NSG-001 has 5 inbound rules. Ports 22, 80, and 443 are allowed from public IPs. The NSG is attached to subnet subnet-production. Compliance status: non-compliant due to unrestricted SSH access.",
  "metadata": {
    "resource_type": "nsg",
    "resource_id": "nsg-001",
    "status": "non_compliant",
    "chunk_type": "evidence_summary|control_description|finding"
  },
  "embedding": {
    "model": "text-embedding-ada-002",
    "vector": [0.123, -0.456, ...],
    "dimension": 1536
  },
  "silver_ref": "silver-{id}",
  "bronze_ref": "bronze-{id}"
}
```

### Chunking Strategy
- **By control**: One or more chunks per control
- **By finding**: Separate chunks for findings, evidence, recommendations
- **Size**: ~500-1000 tokens per chunk
- **Overlap**: 10-20% overlap between chunks for context

### Storage
- **Format**: Vector database (e.g., Azure Cognitive Search, Pinecone, Weaviate)
- **Indexing**: Vector similarity search on embeddings
- **Metadata filtering**: By tenant, domain, control, status

### Use Cases
- RAG retrieval for AI analysis
- Semantic search for related findings
- Context retrieval for report generation
- Similarity search for pattern detection

---

## Domain and Control Framework

### Domain Schema

```json
{
  "domain_code": "NET",
  "domain_name": "Network Security",
  "description": "Network security controls including NSG rules, firewalls, and network segmentation",
  "controls": [
    "SEC-NET-0001",
    "SEC-NET-0002",
    ...
  ]
}
```

### Control Schema

```json
{
  "control_id": "SEC-NET-0007",
  "control_title": "Network Security Group Rules",
  "domain_code": "NET",
  "description": "Ensure NSG rules restrict access to only necessary ports and sources",
  "question": "Are NSG rules configured to restrict access appropriately?",
  "required_evidence": [
    "nsg_rules",
    "allowed_ports",
    "source_addresses"
  ],
  "capability_requirements": [
    {
      "capability_id": "network_segmentation",
      "weight": 1.0,
      "min_strength": 0.7
    }
  ]
}
```

---

## Data Lineage

### Traceability
- **Bronze → Silver**: `evidence.raw_data_ref` links silver to bronze
- **Silver → Gold**: `silver_ref` links gold chunks to silver records
- **Gold → Report**: Report generation references gold chunks

### Audit Trail
- Timestamps at each layer
- Version tracking for normalizers and collectors
- Confidence scores for normalization
- Change history for silver records (if mutable)

---

## Migration and Evolution

### Schema Versioning
- Version bronze/silver schemas
- Support multiple schema versions during migration
- Document breaking changes in ADRs

### Backward Compatibility
- Maintain backward compatibility for queries
- Provide migration scripts for schema updates
- Support gradual migration of existing data

---

## References

- `blueprint.md` — Architecture overview
- `adr/0001-architecture-and-storage.md` — Storage decisions
- `config/frameworks.yaml` — Control and domain definitions

