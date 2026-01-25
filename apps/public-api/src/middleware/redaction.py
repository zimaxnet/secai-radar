"""
Redaction middleware - removes private data from public responses
"""

from typing import Any, Dict


def redact_evidence_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redact private fields from evidence item for public API
    
    Removes:
    - blob_ref (private Azure Storage path)
    - Any internal metadata
    """
    redacted = item.copy()
    
    # Remove private blob references
    if "blob_ref" in redacted:
        del redacted["blob_ref"]
    
    # Remove any other private fields
    private_fields = ["internal_notes", "workspace_id", "submitted_by"]
    for field in private_fields:
        redacted.pop(field, None)
    
    return redacted


def redact_response(data: Any) -> Any:
    """
    Recursively redact private data from response
    """
    if isinstance(data, dict):
        if "evidenceItems" in data:
            data["evidenceItems"] = [redact_evidence_item(item) for item in data["evidenceItems"]]
        if "evidence_items" in data:
            data["evidence_items"] = [redact_evidence_item(item) for item in data["evidence_items"]]
        
        # Recursively process nested dicts
        return {k: redact_response(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [redact_response(item) for item in data]
    else:
        return data
