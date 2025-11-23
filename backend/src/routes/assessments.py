"""
Assessment API Routes
Provides endpoints for controls, tools, gaps, summary, and evidence management
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
import io
import csv
import json
from collections import defaultdict

from ..services.storage import get_storage_service
from ..services.seed_data import get_seed_data_service

router = APIRouter(prefix="/api/tenant/{tenant_id}", tags=["assessments"])


# Pydantic Models
class ControlEntity(BaseModel):
    ControlID: str
    Domain: str
    ControlTitle: Optional[str] = ""
    ControlDescription: Optional[str] = ""
    Question: Optional[str] = ""
    RequiredEvidence: Optional[str] = ""
    Status: Optional[str] = "NotStarted"
    Owner: Optional[str] = ""
    Frequency: Optional[str] = ""
    ScoreNumeric: Optional[float] = 0.0
    Weight: Optional[float] = 0.0
    Notes: Optional[str] = ""
    SourceRef: Optional[str] = ""
    Tags: Optional[str] = ""
    UpdatedAt: Optional[str] = ""


class TenantTool(BaseModel):
    vendorToolId: str
    Enabled: bool = True
    ConfigScore: float = 0.8
    Owner: Optional[str] = ""
    Notes: Optional[str] = ""


class GapAnalysisResult(BaseModel):
    ControlID: str
    DomainPartition: str
    Coverage: float
    HardGaps: List[Dict[str, Any]]
    SoftGaps: List[Dict[str, Any]]
    AIRecommendation: Optional[str] = None


class SummaryResponse(BaseModel):
    byDomain: List[Dict[str, Any]]


# Controls Endpoints
@router.get("/controls")
async def get_controls(
    tenant_id: str,
    domain: Optional[str] = Query(None, description="Filter by domain code"),
    status: Optional[str] = Query(None, description="Filter by status"),
    q: Optional[str] = Query(None, description="Search query")
):
    """Get controls for a tenant"""
    try:
        storage = get_storage_service()
        table = storage.get_controls_table()
        
        if domain:
            partition_key = f"{tenant_id}|{domain}"
            entities = list(table.query_entities(f"PartitionKey eq '{partition_key}'"))
        else:
            entities = [
                e for e in table.list_entities()
                if str(e.get("PartitionKey", "")).startswith(f"{tenant_id}|")
            ]
        
        # Filter by status
        if status:
            entities = [e for e in entities if str(e.get("Status", "")).lower() == status.lower()]
        
        # Search query
        if q:
            q_lower = q.lower()
            def matches(e):
                search_fields = ["ControlTitle", "ControlDescription", "Question", "Notes"]
                return any(q_lower in str(e.get(field, "")).lower() for field in search_fields)
            entities = [e for e in entities if matches(e)]
        
        return {"items": entities, "total": len(entities)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_controls(
    tenant_id: str,
    file: Optional[UploadFile] = File(None),
    body: Optional[List[Dict[str, Any]]] = None
):
    """Import controls from CSV or JSON"""
    try:
        rows = []
        
        if file:
            # Parse CSV
            content = await file.read()
            text = content.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text))
            rows = [dict(row) for row in reader]
        elif body:
            rows = body
        else:
            raise HTTPException(status_code=400, detail="No data provided. Send CSV file or JSON array.")
        
        storage = get_storage_service()
        table = storage.get_controls_table()
        
        inserted = 0
        for row in rows:
            control_id = row.get("ControlID") or ""
            domain = row.get("Domain") or ""
            
            if not control_id or not domain:
                continue
            
            # Derive domain code from ControlID or use provided DomainCode
            domain_code = ""
            if control_id.startswith("SEC-") and "-" in control_id[4:]:
                domain_code = control_id.split("-")[1]
            else:
                domain_code = row.get("DomainCode", "")
            
            if not domain_code:
                continue
            
            entity = {
                "PartitionKey": f"{tenant_id}|{domain_code}",
                "RowKey": control_id,
                "Domain": domain,
                "ControlTitle": row.get("ControlTitle", ""),
                "ControlDescription": row.get("ControlDescription", ""),
                "Question": row.get("Question", ""),
                "RequiredEvidence": row.get("RequiredEvidence", ""),
                "Status": row.get("Status", "NotStarted"),
                "Owner": row.get("Owner", ""),
                "Frequency": row.get("Frequency", ""),
                "ScoreNumeric": float(row.get("ScoreNumeric") or 0) if str(row.get("ScoreNumeric") or "").strip() != "" else 0.0,
                "Weight": float(row.get("Weight") or 0) if str(row.get("Weight") or "").strip() != "" else 0.0,
                "Notes": row.get("Notes", ""),
                "SourceRef": row.get("SourceRef", ""),
                "Tags": row.get("Tags", ""),
                "UpdatedAt": row.get("UpdatedAt", "")
            }
            
            table.upsert_entity(entity)
            inserted += 1
        
        return {"ok": True, "inserted": inserted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Tools Endpoints
@router.get("/tools")
async def get_tenant_tools(tenant_id: str):
    """Get tenant tools inventory"""
    try:
        storage = get_storage_service()
        table = storage.get_tenant_tools_table()
        
        items = [
            dict(e) for e in table.list_entities()
            if e.get("PartitionKey") == tenant_id
        ]
        
        return {"items": items, "total": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools")
async def upsert_tenant_tool(tenant_id: str, tool: TenantTool):
    """Create or update a tenant tool"""
    try:
        storage = get_storage_service()
        table = storage.get_tenant_tools_table()
        
        entity = {
            "PartitionKey": tenant_id,
            "RowKey": tool.vendorToolId,
            "Enabled": tool.Enabled,
            "ConfigScore": tool.ConfigScore,
            "Owner": tool.Owner or "",
            "Notes": tool.Notes or ""
        }
        
        table.upsert_entity(entity)
        return {"ok": True, "item": entity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vendor-tools")
async def get_vendor_tools():
    """Get vendor tools catalog"""
    try:
        seed_service = get_seed_data_service()
        tools = seed_service.get_vendor_tools()
        return {"items": tools, "total": len(tools)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Summary Endpoint
@router.get("/summary")
async def get_summary(tenant_id: str) -> SummaryResponse:
    """Get assessment summary by domain"""
    try:
        storage = get_storage_service()
        table = storage.get_controls_table()
        
        items = [
            e for e in table.list_entities()
            if str(e.get("PartitionKey", "")).startswith(f"{tenant_id}|")
        ]
        
        agg = defaultdict(lambda: {"total": 0, "complete": 0, "inProgress": 0, "notStarted": 0})
        
        for item in items:
            partition_key = str(item.get("PartitionKey", ""))
            if "|" not in partition_key:
                continue
            
            domain = partition_key.split("|", 1)[1]
            agg[domain]["total"] += 1
            
            status = str(item.get("Status", "")).lower()
            if status == "complete":
                agg[domain]["complete"] += 1
            elif status == "inprogress":
                agg[domain]["inProgress"] += 1
            else:
                agg[domain]["notStarted"] += 1
        
        result = [{"domain": d, **v} for d, v in agg.items()]
        return SummaryResponse(byDomain=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Gaps Analysis Endpoint
@router.get("/gaps", response_model=Dict[str, Any])
async def get_gaps(
    tenant_id: str,
    ai: bool = Query(False, description="Include AI recommendations")
):
    """Get gap analysis for tenant controls"""
    try:
        seed_service = get_seed_data_service()
        storage = get_storage_service()
        
        # Load seed data
        tool_cap_map = seed_service.get_tool_capability_map()
        control_reqs_map = seed_service.get_control_requirements_map()
        vendor_tools_dict = seed_service.get_vendor_tools_dict()
        
        # Load tenant tools
        tools_table = storage.get_tenant_tools_table()
        tenant_tools_raw = [
            e for e in tools_table.list_entities()
            if e.get("PartitionKey") == tenant_id
        ]
        
        tenant_tools = {
            e["RowKey"]: float(e.get("ConfigScore", 1.0))
            for e in tenant_tools_raw
            if e.get("Enabled", True)
        }
        
        tenant_tools_list = [
            {
                "id": e["RowKey"],
                "name": vendor_tools_dict.get(e["RowKey"], {}).get("name", e["RowKey"]),
                "configScore": float(e.get("ConfigScore", 1.0))
            }
            for e in tenant_tools_raw
            if e.get("Enabled", True)
        ]
        
        # Load controls
        controls_table = storage.get_controls_table()
        control_rows = [
            e for e in controls_table.list_entities()
            if str(e.get("PartitionKey", "")).startswith(f"{tenant_id}|")
        ]
        
        results = []
        for control in control_rows:
            control_id = control.get("RowKey")
            reqs = control_reqs_map.get(control_id, [])
            
            if not reqs:
                continue
            
            # Calculate coverage and gaps
            coverage_score = 0.0
            sum_w = 0.0
            hard_gaps = []
            soft_gaps = []
            
            for req in reqs:
                cap = req.get("capabilityId")
                w = float(req.get("weight", 0))
                min_s = float(req.get("minStrength", 0))
                sum_w += w
                
                best = 0.0
                best_tool = None
                
                for tool_id, cfg_score in tenant_tools.items():
                    strength = tool_cap_map.get(tool_id, {}).get(cap, 0.0) * cfg_score
                    if strength > best:
                        best = strength
                        best_tool = tool_id
                
                coverage_score += w * best
                
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
            
            result = {
                "ControlID": control_id,
                "DomainPartition": control.get("PartitionKey"),
                "Coverage": round(normalized, 3),
                "HardGaps": hard_gaps,
                "SoftGaps": soft_gaps
            }
            
            # Add AI recommendation if requested
            if ai and (hard_gaps or soft_gaps):
                try:
                    from ..orchestrator import Orchestrator
                    orchestrator = Orchestrator()
                    elena_agent = orchestrator.agents.get("elena")
                    
                    if elena_agent:
                        # Get control title from the control entity
                        control_title = control.get("ControlTitle", control_id)
                        
                        # Generate recommendation using Elena agent
                        recommendation = await elena_agent.generate_recommendation(
                            control_id=control_id,
                            control_title=control_title,
                            hard_gaps=hard_gaps,
                            soft_gaps=soft_gaps,
                            tenant_tools=tenant_tools_list,
                            coverage_score=normalized
                        )
                        result["AIRecommendation"] = recommendation
                    else:
                        result["AIRecommendation"] = None
                    result["AIEnabled"] = True
                except Exception as e:
                    # If AI recommendation fails, continue without it
                    result["AIRecommendation"] = None
                    result["AIError"] = str(e)
                    result["AIEnabled"] = True
            
            results.append(result)
        
        return {
            "items": results,
            "total": len(results),
            "aiEnabled": ai
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

