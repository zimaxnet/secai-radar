"""
Elena Bridges - Relationship Manager Agent

Customer advocacy, business translation, and MCA transition guidance.
"""

from typing import Dict, Any, Optional
from ..state import AssessmentState, HandoffPacket, AgentID
from .base_agent import BaseAgent


class ElenaBridges(BaseAgent):
    """
    Elena Bridges - Relationship Manager.
    Bridges technical and business perspectives.
    """
    
    def __init__(self, model_layer=None, state_manager=None, rag_retriever=None):
        """Initialize Elena Bridges agent"""
        super().__init__(
            agent_id=AgentID.ELENA_BRIDGES.value,
            name="Elena Bridges",
            role="Relationship Manager",
            system_prompt="""You are Elena Bridges, a Relationship Manager.
            You translate technical risks to business consequences and protect customer interests.
            Frame technical decisions in terms of business value and customer impact.""",
            model_layer=model_layer,
            state_manager=state_manager,
            rag_retriever=rag_retriever,
            tools=["assess_business_impact", "validate_migration_plan", "customer_communication", "calculate_downtime"]
        )
    
    async def process_task(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket] = None
    ) -> AssessmentState:
        """
        Process business impact assessment or customer validation task.
        
        Args:
            state: Current assessment state
            handoff: Handoff packet with task details
            
        Returns:
            Updated state
        """
        task_description = handoff.task_description if handoff else "Assess business impact"
        
        if "business" in task_description.lower() or "impact" in task_description.lower():
            return await self._assess_business_impact(state, handoff)
        elif "customer" in task_description.lower() or "validate" in task_description.lower():
            return await self._validate_with_customer(state, handoff)
        elif "downtime" in task_description.lower():
            return await self._calculate_downtime(state, handoff)
        else:
            return await self._general_business_review(state, handoff)
    
    async def _assess_business_impact(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Assess business impact of proposed architecture"""
        # Get architecture design if available
        architecture = state.get("architectural_designs", {}).get("landing_zone", {})
        
        prompt = self.format_prompt(
            "Assess the business impact and downtime requirements for the proposed architecture. "
            "Translate technical risks to business consequences.",
            handoff
        )
        
        if architecture:
            prompt += f"\n\nProposed Architecture:\n{architecture.get('description', '')[:500]}"
        
        prompt += "\n\nConsider:"
        prompt += "\n- Downtime requirements"
        prompt += "\n- Business disruption"
        prompt += "\n- Customer relationship impact"
        prompt += "\n- Regulatory compliance risks"
        prompt += "\n- Cost implications"
        
        result = await self.call_model(prompt, {
            "architecture": architecture,
            "findings": state.get("findings", [])
        })
        
        impact_assessment = result.get("content", "")
        
        # Check for high-impact issues that might cause conflicts
        if "4-hour" in impact_assessment.lower() or "downtime" in impact_assessment.lower():
            # This might trigger a conflict with security requirements
            from ..supervisor import Supervisor
            supervisor = Supervisor(self.state_manager, self.model_layer)
            state = supervisor.detect_conflict(
                state,
                "business_interruption",
                f"High downtime requirement identified: {impact_assessment[:200]}",
                [self.agent_id, AgentID.ARIS_THORNE.value]
            )
        
        # Add event
        state = self.add_event(
            state,
            "Governance",
            "Business Impact Assessment",
            85.0,
            "Assessed business impact of proposed architecture"
        )
        
        # Update agent context
        state = self.update_agent_context(
            state,
            task="business_impact_assessment",
            artifact={"impact_assessment": impact_assessment}
        )
        
        return state
    
    async def _validate_with_customer(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Validate migration plan with customer"""
        migration_plan = state.get("migration_plan", {})
        
        prompt = self.format_prompt(
            "Validate the migration plan and billing structure with the customer. "
            "Ensure alignment with customer expectations and business requirements.",
            handoff
        )
        
        if migration_plan:
            prompt += f"\n\nMigration Plan:\n{migration_plan.get('description', '')[:500]}"
        
        result = await self.call_model(prompt, {
            "migration_plan": migration_plan
        })
        
        validation_result = result.get("content", "")
        
        # Add event
        state = self.add_event(
            state,
            "Governance",
            "Customer Validation",
            90.0,
            "Validated migration plan with customer"
        )
        
        # Update agent context
        state = self.update_agent_context(
            state,
            task="customer_validation",
            artifact={"validation": validation_result}
        )
        
        return state
    
    async def _calculate_downtime(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Calculate downtime requirements"""
        prompt = self.format_prompt(
            "Calculate estimated downtime for the migration activities",
            handoff
        )
        
        result = await self.call_model(prompt, {
            "architecture": state.get("architectural_designs", {})
        })
        
        state = self.add_event(
            state,
            "Governance",
            "Downtime Calculation",
            70.0,
            "Calculated downtime requirements"
        )
        
        return state
    
    async def _general_business_review(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """General business review"""
        prompt = self.format_prompt(
            "Review project from business perspective",
            handoff
        )
        
        result = await self.call_model(prompt)
        
        state = self.add_event(
            state,
            "Governance",
            "Business Review",
            65.0,
            "Business review completed"
        )
        
        return state

