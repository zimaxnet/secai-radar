"""
Phase 2: Design and Conflict Resolution

Workflow:
- Aris proposes architecture
- Elena assesses business impact
- Marcus resolves conflicts if needed
"""

from typing import Dict, Any
from ..state import AssessmentState, AgentID


class DesignPhase:
    """
    Phase 2: Design and Conflict Resolution phase implementation.
    """
    
    @staticmethod
    def is_complete(state: AssessmentState) -> bool:
        """
        Check if design phase is complete.
        
        Args:
            state: Current assessment state
            
        Returns:
            True if phase is complete
        """
        agent_contexts = state.get("agent_contexts", {})
        
        aris_ctx = agent_contexts.get(AgentID.ARIS_THORNE.value)
        elena_ctx = agent_contexts.get(AgentID.ELENA_BRIDGES.value)
        
        # Check if architecture is designed
        architecture_designed = (
            aris_ctx and "architecture_design" in aris_ctx.completed_tasks
        )
        
        # Check if business impact is assessed
        impact_assessed = (
            elena_ctx and "business_impact_assessment" in elena_ctx.completed_tasks
        )
        
        # Check if conflicts are resolved
        conflicts_resolved = len(state.get("active_conflicts", [])) == 0
        
        return architecture_designed and impact_assessed and conflicts_resolved
    
    @staticmethod
    def get_next_task(state: AssessmentState) -> Dict[str, Any]:
        """
        Get the next task for the design phase.
        
        Args:
            state: Current assessment state
            
        Returns:
            Task information dict
        """
        agent_contexts = state.get("agent_contexts", {})
        
        # Check if architecture is designed
        aris_ctx = agent_contexts.get(AgentID.ARIS_THORNE.value)
        if not aris_ctx or "architecture_design" not in aris_ctx.completed_tasks:
            return {
                "agent": AgentID.ARIS_THORNE.value,
                "task": "Design Azure Landing Zone architecture",
                "description": "Design architecture based on assessment findings"
            }
        
        # Check if business impact is assessed
        elena_ctx = agent_contexts.get(AgentID.ELENA_BRIDGES.value)
        if not elena_ctx or "business_impact_assessment" not in elena_ctx.completed_tasks:
            return {
                "agent": AgentID.ELENA_BRIDGES.value,
                "task": "Assess business impact",
                "description": "Evaluate business impact and downtime requirements"
            }
        
        # Check for conflicts
        active_conflicts = state.get("active_conflicts", [])
        if active_conflicts:
            return {
                "agent": AgentID.MARCUS_STERLING.value,
                "task": "Resolve conflicts",
                "description": f"Resolve {len(active_conflicts)} active conflicts"
            }
        
        # Phase complete
        return {
            "agent": None,
            "task": "Phase complete",
            "description": "Design phase completed"
        }

