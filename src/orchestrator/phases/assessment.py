"""
Phase 1: Assessment and Discovery

Workflow:
- Aris queries CAF knowledge base
- Leo analyzes identity
- Ravi scans infrastructure
- Kenji collates findings
"""

from typing import Dict, Any
from ..state import AssessmentState, AgentID


class AssessmentPhase:
    """
    Phase 1: Assessment and Discovery phase implementation.
    """
    
    @staticmethod
    def is_complete(state: AssessmentState) -> bool:
        """
        Check if assessment phase is complete.
        
        Args:
            state: Current assessment state
            
        Returns:
            True if phase is complete
        """
        agent_contexts = state.get("agent_contexts", {})
        
        # Check if all required tasks are completed
        aris_ctx = agent_contexts.get(AgentID.ARIS_THORNE.value)
        leo_ctx = agent_contexts.get(AgentID.LEO_VANCE.value)
        ravi_ctx = agent_contexts.get(AgentID.RAVI_PATEL.value)
        kenji_ctx = agent_contexts.get(AgentID.KENJI_SATO.value)
        
        return (
            aris_ctx and "caf_query" in aris_ctx.completed_tasks and
            leo_ctx and "identity_analysis" in leo_ctx.completed_tasks and
            ravi_ctx and "infrastructure_scan" in ravi_ctx.completed_tasks and
            kenji_ctx and "findings_collation" in kenji_ctx.completed_tasks
        )
    
    @staticmethod
    def get_next_task(state: AssessmentState) -> Dict[str, Any]:
        """
        Get the next task for the assessment phase.
        
        Args:
            state: Current assessment state
            
        Returns:
            Task information dict
        """
        agent_contexts = state.get("agent_contexts", {})
        
        # Check tasks in order
        aris_ctx = agent_contexts.get(AgentID.ARIS_THORNE.value)
        if not aris_ctx or "caf_query" not in aris_ctx.completed_tasks:
            return {
                "agent": AgentID.ARIS_THORNE.value,
                "task": "Query CAF knowledge base for assessment checklist",
                "description": "Query Azure Cloud Adoption Framework knowledge base"
            }
        
        leo_ctx = agent_contexts.get(AgentID.LEO_VANCE.value)
        if not leo_ctx or "identity_analysis" not in leo_ctx.completed_tasks:
            return {
                "agent": AgentID.LEO_VANCE.value,
                "task": "Analyze legacy identity configuration",
                "description": "Analyze identity and map to Entra ID"
            }
        
        ravi_ctx = agent_contexts.get(AgentID.RAVI_PATEL.value)
        if not ravi_ctx or "infrastructure_scan" not in ravi_ctx.completed_tasks:
            return {
                "agent": AgentID.RAVI_PATEL.value,
                "task": "Scan legacy CSP infrastructure",
                "description": "Run security scan of networking and infrastructure"
            }
        
        kenji_ctx = agent_contexts.get(AgentID.KENJI_SATO.value)
        if not kenji_ctx or "findings_collation" not in kenji_ctx.completed_tasks:
            return {
                "agent": AgentID.KENJI_SATO.value,
                "task": "Collate assessment findings",
                "description": "Aggregate findings into status report"
            }
        
        # Phase complete
        return {
            "agent": None,
            "task": "Phase complete",
            "description": "Assessment phase completed"
        }

