"""
Leo Vance - Security Architect (IAM) Agent

Identity migration, RBAC design, and MCA billing role mapping.
"""

from typing import Dict, Any, Optional
from ..state import AssessmentState, HandoffPacket, AgentID
from .base_agent import BaseAgent


class LeoVance(BaseAgent):
    """
    Leo Vance - Security Architect specializing in Identity and Access Management.
    """
    
    def __init__(self, model_layer=None, state_manager=None, rag_retriever=None):
        """Initialize Leo Vance agent"""
        super().__init__(
            agent_id=AgentID.LEO_VANCE.value,
            name="Leo Vance",
            role="Security Architect - Identity & Access",
            system_prompt="""You are Leo Vance, a Security Architect specializing in IAM.
            You design identity solutions, map legacy identities to Entra ID, and ensure proper RBAC.
            Understand MCA billing hierarchy and ensure separation of duties.""",
            model_layer=model_layer,
            state_manager=state_manager,
            rag_retriever=rag_retriever,
            tools=["design_identity_migration", "map_billing_roles", "design_conditional_access", "analyze_legacy_identity"]
        )
    
    async def process_task(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket] = None
    ) -> AssessmentState:
        """
        Process identity and access management task.
        
        Args:
            state: Current assessment state
            handoff: Handoff packet with task details
            
        Returns:
            Updated state
        """
        task_description = handoff.task_description if handoff else "Design identity solution"
        
        if "identity" in task_description.lower() and "analysis" in task_description.lower():
            return await self._analyze_legacy_identity(state, handoff)
        elif "mca" in task_description.lower() or "billing" in task_description.lower():
            return await self._design_mca_billing_hierarchy(state, handoff)
        elif "conditional" in task_description.lower() or "access" in task_description.lower():
            return await self._design_conditional_access(state, handoff)
        else:
            return await self._design_identity_migration(state, handoff)
    
    async def _analyze_legacy_identity(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Analyze legacy identity configuration"""
        prompt = self.format_prompt(
            "Analyze legacy identity configuration and identify gaps. "
            "Map users to Entra ID roles and identify MFA requirements.",
            handoff
        )
        
        result = await self.call_model(prompt, {
            "tenant_id": state.get("tenant_id")
        })
        
        identity_analysis = result.get("content", "")
        
        # Add finding
        finding = {
            "id": f"finding_{len(state.get('findings', [])) + 1}",
            "domain": "Identity",
            "type": "identity_analysis",
            "description": "Legacy identity analysis completed",
            "details": identity_analysis,
            "agent": self.agent_id
        }
        state["findings"].append(finding)
        
        # Add event
        state = self.add_event(
            state,
            "Identity",
            "Identity Analysis",
            85.0,
            "Analyzed legacy identity configuration"
        )
        
        # Update agent context
        state = self.update_agent_context(
            state,
            task="identity_analysis",
            artifact={"analysis": identity_analysis}
        )
        
        return state
    
    async def _design_mca_billing_hierarchy(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Design MCA billing hierarchy and management group structure"""
        # Query RAG for MCA billing guidance
        mca_query = "Microsoft Customer Agreement billing hierarchy Billing Profile Invoice Section"
        rag_context = await self.query_rag(mca_query)
        
        prompt = self.format_prompt(
            "Design MCA billing hierarchy and management group structure. "
            "Map legacy departments to Invoice Sections and ensure proper billing role assignments.",
            handoff,
            rag_context
        )
        
        prompt += "\n\nKey Requirements:"
        prompt += "\n- Map legacy 'Departments' to MCA 'Invoice Sections'"
        prompt += "\n- Design Management Group hierarchy"
        prompt += "\n- Ensure separation between billing roles and technical roles"
        prompt += "\n- Map Billing Account Owner, Billing Profile Owner, Invoice Section Owner roles"
        
        result = await self.call_model(prompt, {
            "tenant_id": state.get("tenant_id")
        })
        
        billing_design = result.get("content", "")
        
        # Store in migration plan
        if "migration_plan" not in state or state["migration_plan"] is None:
            state["migration_plan"] = {}
        
        state["migration_plan"]["billing_hierarchy"] = {
            "description": billing_design,
            "agent": self.agent_id
        }
        
        # Add event
        state = self.add_event(
            state,
            "Governance",
            "MCA Billing Design",
            90.0,
            "Designed MCA billing hierarchy"
        )
        
        # Update agent context
        state = self.update_agent_context(
            state,
            task="mca_billing_design",
            artifact={"billing_design": billing_design}
        )
        
        return state
    
    async def _design_conditional_access(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Design Conditional Access policies"""
        prompt = self.format_prompt(
            "Design Conditional Access policies for the new Azure environment",
            handoff
        )
        
        result = await self.call_model(prompt)
        
        state = self.add_event(
            state,
            "Identity",
            "Conditional Access Design",
            80.0,
            "Designed Conditional Access policies"
        )
        
        return state
    
    async def _design_identity_migration(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Design identity migration plan"""
        prompt = self.format_prompt(
            "Design identity migration plan from legacy identity provider to Entra ID",
            handoff
        )
        
        result = await self.call_model(prompt)
        
        state = self.add_event(
            state,
            "Identity",
            "Identity Migration Design",
            85.0,
            "Designed identity migration plan"
        )
        
        return state

