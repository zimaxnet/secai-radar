"""
Supervisor Node for Multi-Agent Orchestration

Implements hierarchical routing logic to coordinate agent interactions
and manage the workflow phases.
"""

from typing import Dict, Any, Optional
from .state import (
    AssessmentState,
    AssessmentPhase,
    AgentID,
    StateManager,
    HandoffPacket
)


class Supervisor:
    """
    Supervisor node that routes tasks between agents based on workflow phase
    and task requirements.
    """
    
    def __init__(self, state_manager: StateManager, model_layer=None):
        """
        Initialize Supervisor.
        
        Args:
            state_manager: StateManager instance
            model_layer: Model Layer for reasoning about routing
        """
        self.state_manager = state_manager
        self.model_layer = model_layer
    
    def route(self, state: AssessmentState) -> AssessmentState:
        """
        Route tasks to appropriate agents based on current phase and state.
        
        Args:
            state: Current assessment state
            
        Returns:
            Updated state with routing decisions
        """
        phase = state.get("phase", AssessmentPhase.ASSESSMENT)
        
        # Route based on phase
        if phase == AssessmentPhase.ASSESSMENT:
            return self._route_assessment_phase(state)
        elif phase == AssessmentPhase.DESIGN:
            return self._route_design_phase(state)
        elif phase == AssessmentPhase.MIGRATION:
            return self._route_migration_phase(state)
        else:
            # Phase completed
            state["is_complete"] = True
            state["termination_reason"] = "All phases completed"
            return state
    
    def _route_assessment_phase(self, state: AssessmentState) -> AssessmentState:
        """
        Route tasks for Assessment and Discovery phase.
        
        Phase 1 workflow:
        - Aris queries CAF knowledge base
        - Leo analyzes identity
        - Ravi scans infrastructure
        - Kenji collates findings
        """
        # Check if Aris has completed CAF query
        aris_ctx = state["agent_contexts"].get(AgentID.ARIS_THORNE.value)
        if not aris_ctx or "caf_query" not in aris_ctx.completed_tasks:
            # Route to Aris for CAF knowledge base query
            state["current_agent"] = AgentID.ARIS_THORNE.value
            handoff = self.state_manager.create_handoff_packet(
                from_agent=AgentID.SUPERVISOR.value,
                to_agent=AgentID.ARIS_THORNE.value,
                task_description="Query CAF knowledge base for assessment checklist",
                context_summary=f"Starting assessment phase for tenant {state['tenant_id']}"
            )
            state["pending_handoffs"].append(handoff)
            return state
        
        # Check if Leo has analyzed identity
        leo_ctx = state["agent_contexts"].get(AgentID.LEO_VANCE.value)
        if not leo_ctx or "identity_analysis" not in leo_ctx.completed_tasks:
            state["current_agent"] = AgentID.LEO_VANCE.value
            handoff = self.state_manager.create_handoff_packet(
                from_agent=AgentID.SUPERVISOR.value,
                to_agent=AgentID.LEO_VANCE.value,
                task_description="Analyze legacy identity configuration and map to Entra ID",
                context_summary="Identity domain assessment required"
            )
            state["pending_handoffs"].append(handoff)
            return state
        
        # Check if Ravi has scanned infrastructure
        ravi_ctx = state["agent_contexts"].get(AgentID.RAVI_PATEL.value)
        if not ravi_ctx or "infrastructure_scan" not in ravi_ctx.completed_tasks:
            state["current_agent"] = AgentID.RAVI_PATEL.value
            handoff = self.state_manager.create_handoff_packet(
                from_agent=AgentID.SUPERVISOR.value,
                to_agent=AgentID.RAVI_PATEL.value,
                task_description="Scan legacy CSP networking and security configuration",
                context_summary="Infrastructure security assessment required"
            )
            state["pending_handoffs"].append(handoff)
            return state
        
        # Check if Kenji has collated findings
        kenji_ctx = state["agent_contexts"].get(AgentID.KENJI_SATO.value)
        if not kenji_ctx or "findings_collation" not in kenji_ctx.completed_tasks:
            state["current_agent"] = AgentID.KENJI_SATO.value
            handoff = self.state_manager.create_handoff_packet(
                from_agent=AgentID.SUPERVISOR.value,
                to_agent=AgentID.KENJI_SATO.value,
                task_description="Collate assessment findings into status report",
                context_summary="Assessment phase findings need to be aggregated"
            )
            state["pending_handoffs"].append(handoff)
            return state
        
        # Assessment phase complete, transition to Design phase
        state["phase"] = AssessmentPhase.DESIGN
        state["current_agent"] = AgentID.ARIS_THORNE.value
        return state
    
    def _route_design_phase(self, state: AssessmentState) -> AssessmentState:
        """
        Route tasks for Design and Conflict Resolution phase.
        
        Phase 2 workflow:
        - Aris proposes architecture
        - Elena assesses business impact
        - Marcus resolves conflicts if needed
        """
        # Check if Aris has proposed architecture
        aris_ctx = state["agent_contexts"].get(AgentID.ARIS_THORNE.value)
        if not aris_ctx or "architecture_design" not in aris_ctx.completed_tasks:
            state["current_agent"] = AgentID.ARIS_THORNE.value
            handoff = self.state_manager.create_handoff_packet(
                from_agent=AgentID.SUPERVISOR.value,
                to_agent=AgentID.ARIS_THORNE.value,
                task_description="Design Azure Landing Zone architecture based on assessment findings",
                context_summary=f"Assessment findings: {len(state['findings'])} findings identified"
            )
            state["pending_handoffs"].append(handoff)
            return state
        
        # Check if Elena has assessed business impact
        elena_ctx = state["agent_contexts"].get(AgentID.ELENA_BRIDGES.value)
        if not elena_ctx or "business_impact_assessment" not in elena_ctx.completed_tasks:
            state["current_agent"] = AgentID.ELENA_BRIDGES.value
            handoff = self.state_manager.create_handoff_packet(
                from_agent=AgentID.SUPERVISOR.value,
                to_agent=AgentID.ELENA_BRIDGES.value,
                task_description="Assess business impact and downtime requirements for proposed architecture",
                context_summary="Architecture design needs business impact review"
            )
            state["pending_handoffs"].append(handoff)
            return state
        
        # Check for conflicts
        if state.get("active_conflicts"):
            # Route to Marcus for conflict resolution
            state["current_agent"] = AgentID.MARCUS_STERLING.value
            handoff = self.state_manager.create_handoff_packet(
                from_agent=AgentID.SUPERVISOR.value,
                to_agent=AgentID.MARCUS_STERLING.value,
                task_description="Resolve conflicts between security requirements and business constraints",
                context_summary=f"Active conflicts: {len(state['active_conflicts'])} conflicts require resolution"
            )
            state["pending_handoffs"].append(handoff)
            return state
        
        # Design phase complete, transition to Migration phase
        state["phase"] = AssessmentPhase.MIGRATION
        state["current_agent"] = AgentID.LEO_VANCE.value
        return state
    
    def _route_migration_phase(self, state: AssessmentState) -> AssessmentState:
        """
        Route tasks for Migration Planning phase.
        
        Phase 3 workflow:
        - Leo designs MCA billing hierarchy
        - Elena validates with customer
        - Final report generation
        """
        # Check if Leo has designed MCA billing hierarchy
        leo_ctx = state["agent_contexts"].get(AgentID.LEO_VANCE.value)
        if not leo_ctx or "mca_billing_design" not in leo_ctx.completed_tasks:
            state["current_agent"] = AgentID.LEO_VANCE.value
            handoff = self.state_manager.create_handoff_packet(
                from_agent=AgentID.SUPERVISOR.value,
                to_agent=AgentID.LEO_VANCE.value,
                task_description="Design MCA billing hierarchy and management group structure",
                context_summary="Migration planning requires MCA billing alignment"
            )
            state["pending_handoffs"].append(handoff)
            return state
        
        # Check if Elena has validated with customer
        elena_ctx = state["agent_contexts"].get(AgentID.ELENA_BRIDGES.value)
        if not elena_ctx or "customer_validation" not in elena_ctx.completed_tasks:
            state["current_agent"] = AgentID.ELENA_BRIDGES.value
            handoff = self.state_manager.create_handoff_packet(
                from_agent=AgentID.SUPERVISOR.value,
                to_agent=AgentID.ELENA_BRIDGES.value,
                task_description="Validate migration plan and billing structure with customer",
                context_summary="Customer validation required before finalizing migration plan"
            )
            state["pending_handoffs"].append(handoff)
            return state
        
        # Migration phase complete
        state["phase"] = AssessmentPhase.COMPLETED
        state["is_complete"] = True
        state["termination_reason"] = "All migration planning phases completed"
        return state
    
    def detect_conflict(
        self,
        state: AssessmentState,
        conflict_type: str,
        description: str,
        involved_agents: list
    ) -> AssessmentState:
        """
        Detect and record a conflict between agents.
        
        Args:
            state: Current assessment state
            conflict_type: Type of conflict (e.g., "budget", "timeline", "security")
            description: Conflict description
            involved_agents: List of agent IDs involved in conflict
            
        Returns:
            Updated state with conflict recorded
        """
        conflict = {
            "id": f"conflict_{len(state.get('active_conflicts', [])) + 1}",
            "type": conflict_type,
            "description": description,
            "involved_agents": involved_agents,
            "detected_at": state["updated_at"].isoformat() if isinstance(state["updated_at"], type(state["updated_at"])) else str(state["updated_at"]),
            "status": "active"
        }
        
        state["active_conflicts"].append(conflict)
        state["updated_at"] = state["updated_at"]  # Trigger update
        
        return state
    
    def resolve_conflict(
        self,
        state: AssessmentState,
        conflict_id: str,
        resolution: str,
        resolved_by: str
    ) -> AssessmentState:
        """
        Resolve a conflict and move it to resolved conflicts.
        
        Args:
            state: Current assessment state
            conflict_id: Conflict identifier
            resolution: Resolution description
            resolved_by: Agent ID that resolved the conflict
            
        Returns:
            Updated state with conflict resolved
        """
        # Find and move conflict
        for i, conflict in enumerate(state["active_conflicts"]):
            if conflict["id"] == conflict_id:
                conflict["status"] = "resolved"
                conflict["resolution"] = resolution
                conflict["resolved_by"] = resolved_by
                conflict["resolved_at"] = state["updated_at"].isoformat() if isinstance(state["updated_at"], type(state["updated_at"])) else str(state["updated_at"])
                
                state["resolved_conflicts"].append(conflict)
                state["active_conflicts"].pop(i)
                break
        
        state["updated_at"] = state["updated_at"]  # Trigger update
        
        return state

