"""
SecAI Radar Scoring Engine

Provides deterministic, rule-based scoring for control coverage based on 
capability requirements and tenant tool inventory.
"""

from typing import Dict, List, Tuple


def compute_control_coverage(
    reqs: List[Dict],
    tenant_tools: Dict[str, float],
    toolcap: Dict[str, Dict[str, float]]
) -> Tuple[float, List[Dict], List[Dict]]:
    """
    Compute control coverage score based on capability requirements and available tools.
    
    This is the core scoring algorithm for SecAI Radar. For each control:
    1. Identify required capabilities with weights and minimum strengths
    2. Find the best tool covering each capability (strength × configScore)
    3. Compute weighted coverage score
    4. Classify hard gaps (missing capabilities) and soft gaps (below threshold)
    
    Args:
        reqs: List of capability requirements, each containing:
            - capabilityId: str - The capability identifier
            - weight: float - Weight of this capability (0.0-1.0)
            - minStrength: float - Minimum required strength threshold
        tenant_tools: Dict mapping tool IDs to their configuration scores (0.0-1.0)
        toolcap: Nested dict mapping tool IDs to capability strengths:
            {toolId: {capabilityId: strength}}
    
    Returns:
        Tuple of (normalized_coverage, hard_gaps, soft_gaps):
            - normalized_coverage: float - Overall coverage score (0.0-1.0)
            - hard_gaps: List of capabilities with zero coverage
            - soft_gaps: List of capabilities below minimum threshold
    
    Example:
        >>> reqs = [{"capabilityId": "siem", "weight": 0.6, "minStrength": 0.7}]
        >>> tools = {"google-secops": 0.8}
        >>> toolcap = {"google-secops": {"siem": 0.9}}
        >>> coverage, hard, soft = compute_control_coverage(reqs, tools, toolcap)
        >>> print(f"Coverage: {coverage:.2f}")  # Output: Coverage: 0.72
    """
    coverage_score = 0.0
    sum_w = 0.0
    hard_gaps: List[Dict] = []
    soft_gaps: List[Dict] = []

    for r in reqs:
        cap = r["capabilityId"]
        w = float(r.get("weight", 0))
        min_s = float(r.get("minStrength", 0))
        sum_w += w
        
        # Find best tool for this capability
        best = 0.0
        best_tool = None
        for tool_id, cfg in tenant_tools.items():
            strength = float(toolcap.get(tool_id, {}).get(cap, 0.0))
            effective_strength = strength * float(cfg)
            if effective_strength > best:
                best = effective_strength
                best_tool = tool_id
        
        coverage_score += w * best
        
        # Classify gaps
        if best == 0.0:
            hard_gaps.append({"capabilityId": cap, "weight": w})
        elif best < min_s:
            soft_gaps.append({
                "capabilityId": cap,
                "weight": w,
                "best": best,
                "min": min_s,
                "tool": best_tool
            })

    normalized = (coverage_score / sum_w) if sum_w > 0 else 0.0
    return normalized, hard_gaps, soft_gaps
