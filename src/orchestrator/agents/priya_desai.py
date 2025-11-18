"""
Priya Desai - Senior Program Manager (Offshore Lead) Agent

Delivery assurance, quality control, and offshore team management.
"""

from typing import Dict, Any, Optional
from ..state import AssessmentState, HandoffPacket, AgentID
from .base_agent import BaseAgent


class PriyaDesai(BaseAgent):
    """
    Priya Desai - Senior Program Manager leading offshore engineering team.
    """
    
    def __init__(self, model_layer=None, state_manager=None, rag_retriever=None):
        """Initialize Priya Desai agent"""
        super().__init__(
            agent_id=AgentID.PRIYA_DESAI.value,
            name="Priya Desai",
            role="Senior Program Manager - Offshore Lead",
            system_prompt="""You are Priya Desai, a Senior Program Manager.
            You ensure quality delivery and efficient execution. Maintain high quality standards
            and clear communication between onshore and offshore teams.""",
            model_layer=model_layer,
            state_manager=state_manager,
            rag_retriever=rag_retriever,
            tools=["review_code", "assign_tasks", "quality_gate", "approve_for_onshore"]
        )
    
    async def process_task(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket] = None
    ) -> AssessmentState:
        """
        Process quality review or task assignment.
        
        Args:
            state: Current assessment state
            handoff: Handoff packet with task details
            
        Returns:
            Updated state
        """
        task_description = handoff.task_description if handoff else "Review work quality"
        
        if "review" in task_description.lower() or "quality" in task_description.lower():
            return await self._review_work(state, handoff)
        elif "assign" in task_description.lower():
            return await self._assign_tasks(state, handoff)
        else:
            return await self._general_quality_review(state, handoff)
    
    async def _review_work(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Review code or documentation for quality"""
        prompt = self.format_prompt(
            "Review the work for quality, standards compliance, and completeness. "
            "Provide approval or rejection with clear feedback.",
            handoff
        )
        
        result = await self.call_model(prompt)
        
        review_result = result.get("content", "")
        
        # Determine approval status (simplified - in production would parse structured response)
        approved = "approved" in review_result.lower() or "pass" in review_result.lower()
        
        # Add event
        state = self.add_event(
            state,
            "Governance",
            "Quality Review",
            75.0,
            f"Quality review: {'Approved' if approved else 'Needs revision'}"
        )
        
        # Update agent context
        state = self.update_agent_context(
            state,
            task="quality_review",
            artifact={"review": review_result, "approved": approved}
        )
        
        return state
    
    async def _assign_tasks(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Assign tasks to offshore engineers"""
        prompt = self.format_prompt(
            "Assign tasks from the backlog to appropriate engineers",
            handoff
        )
        
        result = await self.call_model(prompt)
        
        state = self.add_event(
            state,
            "Governance",
            "Task Assignment",
            70.0,
            "Assigned tasks to offshore team"
        )
        
        return state
    
    async def _general_quality_review(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """General quality review"""
        prompt = self.format_prompt(
            "Review overall project quality and delivery status",
            handoff
        )
        
        result = await self.call_model(prompt)
        
        state = self.add_event(
            state,
            "Governance",
            "Quality Review",
            65.0,
            "General quality review completed"
        )
        
        return state

