from typing import Dict, List, Tuple

# Types
# reqs: list of { capabilityId, weight, minStrength }
# tenant_tools: { toolId: configScore }
# toolcap: { toolId: { capabilityId: strength } }

def compute_control_coverage(reqs: List[Dict], tenant_tools: Dict[str, float], toolcap: Dict[str, Dict[str, float]]):
    coverage_score = 0.0
    sum_w = 0.0
    hard_gaps = []
    soft_gaps = []

    for r in reqs:
        cap = r["capabilityId"]
        w = float(r.get("weight", 0))
        min_s = float(r.get("minStrength", 0))
        sum_w += w
        best = 0.0
        best_tool = None
        for tool_id, cfg in tenant_tools.items():
            s = float(toolcap.get(tool_id, {}).get(cap, 0.0)) * float(cfg)
            if s > best:
                best = s
                best_tool = tool_id
        coverage_score += w * best
        if best == 0.0:
            hard_gaps.append({"capabilityId": cap, "weight": w})
        elif best < min_s:
            soft_gaps.append({"capabilityId": cap, "weight": w, "best": best, "min": min_s, "tool": best_tool})

    normalized = (coverage_score / sum_w) if sum_w > 0 else 0.0
    return normalized, hard_gaps, soft_gaps
