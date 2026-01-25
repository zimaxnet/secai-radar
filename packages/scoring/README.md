# Scoring Package

Trust Score v1 calculation library (Python)

## Responsibilities
- Implement domain subscores (D1-D6)
- Implement weighted Trust Score (0-100)
- Implement tier assignment (A/B/C/D)
- Implement Evidence Confidence (0-3)
- Implement fail-fast flag detection
- Implement risk flag detection
- Generate explainability payload

## Usage
```python
from scoring import calculate_trust_score

score = calculate_trust_score(evidence_items, claims)
```
