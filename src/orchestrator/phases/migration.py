"""
Phase 3: Migration Planning

Workflow:
- Leo designs MCA billing hierarchy
- Elena validates with customer
- Final report generation
"""

from typing import Dict, Any
from ..state import AssessmentState, AgentID


class MigrationPhase:
    """
    Phase 3: Migration Planning phase implementation.
    """
    
    @staticmethod
    def is_complete(state: AssessmentState) -> bool:
        """
        Check if migration phase is complete.
        
        Args:
            state: Current assessment state
            
        Returns:
            True if phase is complete
        """
        agent_contexts = state.get("agent_contexts", {})
        
        leo_ctx = agent_contexts.get(AgentID.LEO_VANCE.value)
        elena_ctx = agent_contexts.get(AgentID.ELENA_BRIDGES.value)
        
        # Check if MCA billing is designed
        billing_designed = (
            leo_ctx and "mca_billing_design" in leo_ctx.completed_tasks
        )
        
        # Check if customer validation is done
        customer_validated = (
            elena_ctx and "customer_validation" in elena_ctx.completed_tasks
        )
        
        return billing_designed and customer_validated
    
    @staticmethod
    def get_next_task(state: AssessmentState) -> Dict[str, Any]:
        """
        Get the next task for the migration phase.
        
        Args:
            state: Current assessment state
            
        Returns:
            Task information dict
        """
        agent_contexts = state.get("agent_contexts", {})
        
        # Check if MCA billing is designed
        leo_ctx = agent_contexts.get(AgentID.LEO_VANCE.value)
        if not leo_ctx or "mca_billing_design" not in leo_ctx.completed_tasks:
            return {
                "agent": AgentID.LEO_VANCE.value,
                "task": "Design MCA billing hierarchy",
                "description": "Design MCA billing structure and management groups"
            }
        
        # Check if customer validation is done
        elena_ctx = agent_contexts.get(AgentID.ELENA_BRIDGES.value)
        if not elena_ctx or "customer_validation" not in elena_ctx.completed_tasks:
            return {
                "agent": AgentID.ELENA_BRIDGES.value,
                "task": "Validate with customer",
                "description": "Validate migration plan with customer"
            }
        
        # Phase complete
        return {
            "agent": None,
            "task": "Phase complete",
            "description": "Migration planning phase completed"
        }

