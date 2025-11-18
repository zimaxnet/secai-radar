"""
Marcus Sterling - Senior Manager Agent

Executive decision-making, conflict resolution, and project leadership.
"""

from typing import Dict, Any, Optional
from ..state import AssessmentState, HandoffPacket, AgentID
from .base_agent import BaseAgent


class MarcusSterling(BaseAgent):
    """
    Marcus Sterling - Senior Manager and Project Lead.
    Makes executive decisions and resolves conflicts.
    """
    
    def __init__(self, model_layer=None, state_manager=None, rag_retriever=None):
        """Initialize Marcus Sterling agent"""
        super().__init__(
            agent_id=AgentID.MARCUS_STERLING.value,
            name="Marcus Sterling",
            role="Senior Manager - Project Lead",
            system_prompt="""You are Marcus Sterling, a Senior Manager and Project Lead.
            Your role is to make executive decisions, resolve conflicts, and ensure project success.
            Focus on the Iron Triangle: Scope, Cost, Time. Be decisive and action-oriented.""",
            model_layer=model_layer,
            state_manager=state_manager,
            rag_retriever=rag_retriever,
            tools=["approve_budget", "resolve_conflict", "phase_transition", "approve_architecture"]
        )
    
    async def process_task(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket] = None
    ) -> AssessmentState:
        """
        Process executive decision or conflict resolution task.
        
        Args:
            state: Current assessment state
            handoff: Handoff packet with task details
            
        Returns:
            Updated state
        """
        task_description = handoff.task_description if handoff else "Review project status and make decisions"
        
        # Check for conflicts that need resolution
        if state.get("active_conflicts"):
            return await self._resolve_conflicts(state, handoff)
        
        # Check for budget approvals needed
        if "budget" in task_description.lower() or "approve" in task_description.lower():
            return await self._handle_budget_approval(state, handoff)
        
        # General executive review
        return await self._executive_review(state, handoff)
    
    async def _resolve_conflicts(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Resolve active conflicts"""
        conflicts = state.get("active_conflicts", [])
        
        if not conflicts:
            return state
        
        # Get conflict details
        conflict = conflicts[0]
        
        # Build prompt for conflict resolution
        prompt = self.format_prompt(
            f"Resolve the following conflict: {conflict.get('description', 'Unknown conflict')}",
            handoff
        )
        
        prompt += f"\n\nConflict Type: {conflict.get('type', 'unknown')}"
        prompt += f"\nInvolved Agents: {', '.join(conflict.get('involved_agents', []))}"
        prompt += f"\nCurrent Budget Remaining: ${state.get('budget_remaining', 0):,.2f}"
        
        # Call model for resolution decision
        result = await self.call_model(prompt, {
            "conflicts": conflicts,
            "budget": state.get("budget_remaining"),
            "phase": state.get("phase")
        })
        
        # Extract resolution from model response
        resolution_text = result.get("content", "")
        
        # Update state with resolution
        from ..supervisor import Supervisor
        supervisor = Supervisor(self.state_manager, self.model_layer)
        state = supervisor.resolve_conflict(
            state,
            conflict["id"],
            resolution_text,
            self.agent_id
        )
        
        # Add event
        state = self.add_event(
            state,
            "Governance",
            "Conflict Resolution",
            85.0,
            f"Resolved conflict: {conflict.get('type', 'unknown')}"
        )
        
        # Update agent context
        state = self.update_agent_context(
            state,
            task=f"resolved_conflict_{conflict['id']}",
            artifact={"resolution": resolution_text, "conflict_id": conflict["id"]}
        )
        
        return state
    
    async def _handle_budget_approval(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Handle budget approval requests"""
        prompt = self.format_prompt(
            "Review budget request and make approval decision",
            handoff
        )
        
        prompt += f"\n\nCurrent Budget: ${state.get('budget', 0):,.2f}"
        prompt += f"Budget Remaining: ${state.get('budget_remaining', 0):,.2f}"
        
        result = await self.call_model(prompt, {
            "budget": state.get("budget"),
            "budget_remaining": state.get("budget_remaining")
        })
        
        # Parse approval decision (simplified - in production would extract structured data)
        decision_text = result.get("content", "")
        
        # Add event
        state = self.add_event(
            state,
            "Governance",
            "Budget Approval",
            90.0,
            f"Budget decision: {decision_text[:100]}"
        )
        
        state = self.update_agent_context(
            state,
            task="budget_approval",
            artifact={"decision": decision_text}
        )
        
        return state
    
    async def _executive_review(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """General executive review of project status"""
        prompt = self.format_prompt(
            "Review overall project status and provide executive summary",
            handoff
        )
        
        prompt += f"\n\nCurrent Phase: {state.get('phase')}"
        prompt += f"Budget Remaining: ${state.get('budget_remaining', 0):,.2f}"
        prompt += f"Critical Risks: {len(state.get('critical_risks', []))}"
        
        result = await self.call_model(prompt, {
            "phase": state.get("phase"),
            "budget_remaining": state.get("budget_remaining"),
            "critical_risks": state.get("critical_risks", [])
        })
        
        state = self.add_event(
            state,
            "Governance",
            "Executive Review",
            75.0,
            "Executive status review completed"
        )
        
        return state

