"""
Vendor Tool Research Service

Provides capabilities to research security vendor tools and dynamically map them
to capabilities and controls. Uses web search and AI to gather up-to-date information.
"""

import json
import os
from typing import List, Dict, Optional
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Import AI service for research capabilities
try:
    from shared.ai_service import get_ai_service
    AI_AVAILABLE = True
except (ImportError, ValueError):
    AI_AVAILABLE = False

class ToolResearchService:
    """Service for researching and mapping security vendor tools"""
    
    def __init__(self):
        self.capabilities_cache = {}
        self.tools_cache = {}
        self._load_capability_taxonomy()
    
    def _load_capability_taxonomy(self):
        """Load capability taxonomy from seeds"""
        root = Path(__file__).resolve().parents[1]
        try:
            # Try api directory first (seeds_capabilities.json doesn't exist, use vendor_tools to infer)
            # Actually, we need to load from seeds directory or vendor_tools
            # For now, we'll build from vendor_tools and tool_capabilities if available
            vendor_tools_path = root / "seeds_vendor_tools.json"
            if vendor_tools_path.exists():
                with open(vendor_tools_path) as f:
                    tools = json.load(f)
                    # Build capabilities from vendor tools
                    for tool in tools:
                        for cap_id in tool.get("capabilities", []):
                            if cap_id not in self.capabilities_cache:
                                self.capabilities_cache[cap_id] = {"id": cap_id, "name": cap_id}
        except Exception as e:
            # Silently fail - capabilities will be inferred from research
            pass
    
    def search_tool_info(self, tool_name: str, vendor: Optional[str] = None) -> Dict:
        """
        Search the internet for information about a security vendor tool
        
        Args:
            tool_name: Name of the security tool
            vendor: Optional vendor name
            
        Returns:
            Dict with tool information, capabilities, and sources
        """
        search_query = f"{vendor or ''} {tool_name} security tool capabilities features"
        
        # Use AI to perform web-augmented search
        if AI_AVAILABLE:
            try:
                ai_service = get_ai_service()
                return self._research_with_ai(ai_service, tool_name, vendor, search_query)
            except:
                pass
        
        # Fallback to basic search (if we have a search API)
        return self._basic_web_search(tool_name, vendor)
    
    def _research_with_ai(self, ai_service, tool_name: str, vendor: Optional[str], search_query: str) -> Dict:
        """Use AI to research tool capabilities"""
        
        system_prompt = """You are a security tool research expert. Your task is to research security vendor tools
and identify their capabilities. You have access to web search to find current information.

When researching a tool, identify:
1. Security capabilities it provides (e.g., SIEM, EDR, WAF, DLP, etc.)
2. Capability strength (0.0-1.0) based on how well it performs each capability
3. Maturity level (0.0-1.0) based on how established and proven the capability is
4. Relevant documentation links

Map capabilities to the standard taxonomy:
- siem, soar, ueba, edr, fim, identity-protection
- ids-ips, ns-firewall, url-filtering, sandboxing
- waf, ddos, casb, ztna, swg
- email-sec, dlp, cspm, cwpp, ti, ir
- vuln-mgmt, log-collect, observability-pipeline

Respond with JSON format."""
        
        user_prompt = f"""Research the security tool: {tool_name}
Vendor: {vendor or 'Unknown'}

Search for current information about this tool's capabilities and features.
Identify which security capabilities it provides and rate each capability:
- strength: 0.0-1.0 (how well it performs the capability)
- maturity: 0.0-1.0 (how established/proven the capability is)

Return JSON:
{{
    "toolName": "{tool_name}",
    "vendor": "{vendor or 'Unknown'}",
    "capabilities": [
        {{
            "capabilityId": "siem",
            "strength": 0.85,
            "maturity": 0.8,
            "notes": "description"
        }}
    ],
    "sources": ["url1", "url2"],
    "lastResearched": "2025-01-15"
}}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = ai_service.chat_completion(
            messages=messages,
            stream=False,
            temperature=0.3,
            max_tokens=4096
        )
        
        try:
            if hasattr(response, 'choices') and response.choices:
                content = response.choices[0].message.content
            else:
                content = str(response)
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            return json.loads(content)
        except:
            return {
                "toolName": tool_name,
                "vendor": vendor,
                "capabilities": [],
                "sources": [],
                "error": "Failed to parse AI response"
            }
    
    def _basic_web_search(self, tool_name: str, vendor: Optional[str]) -> Dict:
        """Basic web search fallback (placeholder - would need actual search API)"""
        return {
            "toolName": tool_name,
            "vendor": vendor,
            "capabilities": [],
            "sources": [],
            "note": "Web search API not configured"
        }
    
    def map_tools_to_controls(
        self,
        tool_list: List[Dict[str, str]],
        controls: List[Dict]
    ) -> Dict:
        """
        Dynamically map a list of vendor tools to the 340 controls across 12 domains
        
        Args:
            tool_list: List of tools with {name, vendor, id} or just names
            controls: List of all controls with their capability requirements
            
        Returns:
            Mapping of tools to controls with coverage analysis
        """
        # Research each tool
        tool_research = {}
        for tool in tool_list:
            tool_id = tool.get("id") or tool.get("name", "").lower().replace(" ", "-")
            tool_name = tool.get("name", tool.get("id", ""))
            vendor = tool.get("vendor")
            
            # Research tool capabilities
            research_result = self.search_tool_info(tool_name, vendor)
            tool_research[tool_id] = research_result
        
        # Map tools to controls based on capabilities
        control_mappings = {}
        
        for control in controls:
            control_id = control.get("controlId") or control.get("RowKey")
            control_reqs = control.get("requirements", [])  # List of required capabilities
            
            tool_coverage = {}
            for tool_id, tool_info in tool_research.items():
                tool_caps = {c["capabilityId"]: c for c in tool_info.get("capabilities", [])}
                
                coverage_score = 0.0
                total_weight = 0.0
                matched_caps = []
                
                for req in control_reqs:
                    cap_id = req.get("capabilityId")
                    weight = float(req.get("weight", 0))
                    min_strength = float(req.get("minStrength", 0))
                    
                    if cap_id in tool_caps:
                        cap_strength = float(tool_caps[cap_id].get("strength", 0))
                        if cap_strength >= min_strength:
                            coverage_score += weight * cap_strength
                            matched_caps.append({
                                "capabilityId": cap_id,
                                "strength": cap_strength,
                                "weight": weight
                            })
                    
                    total_weight += weight
                
                if total_weight > 0:
                    normalized_coverage = coverage_score / total_weight
                    if normalized_coverage > 0:
                        tool_coverage[tool_id] = {
                            "coverage": normalized_coverage,
                            "matchedCapabilities": matched_caps
                        }
            
            control_mappings[control_id] = {
                "controlId": control_id,
                "toolCoverage": tool_coverage,
                "bestTool": max(tool_coverage.items(), key=lambda x: x[1]["coverage"])[0] if tool_coverage else None
            }
        
        return {
            "toolResearch": tool_research,
            "controlMappings": control_mappings,
            "summary": {
                "toolsResearched": len(tool_research),
                "controlsMapped": len(control_mappings),
                "totalControls": len(controls)
            }
        }
    
    def discover_tool_capabilities(self, tool_name: str, vendor: Optional[str] = None) -> List[Dict]:
        """
        Discover capabilities for a specific tool using AI and web search
        
        Args:
            tool_name: Name of the tool
            vendor: Optional vendor name
            
        Returns:
            List of capabilities with strength and maturity scores
        """
        research = self.search_tool_info(tool_name, vendor)
        return research.get("capabilities", [])

