"""
Seed Data Management
Loads and manages framework seed data (control requirements, tool capabilities, etc.)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

# Path to seeds directory (in archive_v1/seeds for now, can be moved later)
SEEDS_BASE = Path(__file__).resolve().parents[2] / "archive_v1" / "seeds"


class SeedDataService:
    """Service for loading and querying seed data"""
    
    def __init__(self, seeds_path: Optional[Path] = None):
        self.seeds_path = seeds_path or SEEDS_BASE
        self._tool_capabilities: Optional[List[Dict]] = None
        self._control_requirements: Optional[List[Dict]] = None
        self._vendor_tools: Optional[List[Dict]] = None
        self._domain_codes: Optional[List[Dict]] = None
        self._capabilities: Optional[List[Dict]] = None
    
    def _load_json(self, filename: str) -> List[Dict]:
        """Load a JSON file from seeds directory"""
        file_path = self.seeds_path / filename
        if not file_path.exists():
            # Try without .json extension
            file_path = self.seeds_path / f"{filename}.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Seed file not found: {filename}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_tool_capabilities(self) -> List[Dict]:
        """Get tool capabilities catalog"""
        if self._tool_capabilities is None:
            self._tool_capabilities = self._load_json("tool_capabilities.json")
        return self._tool_capabilities
    
    def get_control_requirements(self) -> List[Dict]:
        """Get control requirements framework"""
        if self._control_requirements is None:
            self._control_requirements = self._load_json("control_requirements.json")
        return self._control_requirements
    
    def get_vendor_tools(self) -> List[Dict]:
        """Get vendor tools catalog"""
        if self._vendor_tools is None:
            self._vendor_tools = self._load_json("vendor_tools.json")
        return self._vendor_tools
    
    def get_domain_codes(self) -> List[Dict]:
        """Get domain code mappings"""
        if self._domain_codes is None:
            try:
                self._domain_codes = self._load_json("domain_codes.json")
            except FileNotFoundError:
                self._domain_codes = []
        return self._domain_codes
    
    def get_capabilities(self) -> List[Dict]:
        """Get capabilities catalog"""
        if self._capabilities is None:
            try:
                self._capabilities = self._load_json("capabilities.json")
            except FileNotFoundError:
                self._capabilities = []
        return self._capabilities
    
    def get_tool_capability_map(self) -> Dict[str, Dict[str, float]]:
        """
        Returns a map: {vendorToolId: {capabilityId: strength}}
        """
        tool_caps = self.get_tool_capabilities()
        result = defaultdict(dict)
        for tc in tool_caps:
            tool_id = tc.get("vendorToolId", "")
            cap_id = tc.get("capabilityId", "")
            strength = float(tc.get("strength", 0))
            if tool_id and cap_id:
                result[tool_id][cap_id] = strength
        return dict(result)
    
    def get_control_requirements_map(self) -> Dict[str, List[Dict]]:
        """
        Returns a map: {controlId: [requirement1, requirement2, ...]}
        """
        reqs = self.get_control_requirements()
        result = defaultdict(list)
        for req in reqs:
            control_id = req.get("controlId", "")
            if control_id:
                result[control_id].append(req)
        return dict(result)
    
    def get_vendor_tools_dict(self) -> Dict[str, Dict]:
        """
        Returns a map: {toolId: toolData}
        """
        tools = self.get_vendor_tools()
        return {t.get("id", ""): t for t in tools if t.get("id")}


# Singleton instance
_seed_data_service: Optional[SeedDataService] = None


def get_seed_data_service() -> SeedDataService:
    """Get or create the seed data service instance"""
    global _seed_data_service
    if _seed_data_service is None:
        _seed_data_service = SeedDataService()
    return _seed_data_service

