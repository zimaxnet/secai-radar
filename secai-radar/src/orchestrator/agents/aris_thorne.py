"""
Dr. Aris Thorne - Principal Security Architect Agent

CAF alignment, security strategy, and architectural design.
"""

from typing import Dict, Any, Optional
from ..state import AssessmentState, HandoffPacket, AgentID
from .base_agent import BaseAgent


class ArisThorne(BaseAgent):
    """
    Dr. Aris Thorne - Principal Security Architect.
    Designs security architecture aligned with Azure CAF.
    """
    
    def __init__(self, model_layer=None, state_manager=None, rag_retriever=None):
        """Initialize Aris Thorne agent"""
        super().__init__(
            agent_id=AgentID.ARIS_THORNE.value,
            name="Dr. Aris Thorne",
            role="Principal Security Architect",
            system_prompt="""You are Dr. Aris Thorne, a Principal Security Architect.
            You are uncompromising on security standards and strictly adhere to Azure CAF principles.
            Design for Zero Trust security model and provide detailed architectural blueprints.""",
            model_layer=model_layer,
            state_manager=state_manager,
            rag_retriever=rag_retriever,
            tools=["query_caf_knowledge", "design_landing_zone", "threat_modeling", "generate_architecture_blueprint"]
        )
    
    async def process_task(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket] = None
    ) -> AssessmentState:
        """
        Process security architecture task.
        
        Args:
            state: Current assessment state
            handoff: Handoff packet with task details
            
        Returns:
            Updated state
        """
        task_description = handoff.task_description if handoff else "Design security architecture"
        
        # Check task type
        if "caf" in task_description.lower() or "knowledge" in task_description.lower():
            return await self._query_caf_knowledge(state, handoff)
        elif "design" in task_description.lower() or "architecture" in task_description.lower():
            return await self._design_architecture(state, handoff)
        elif "threat" in task_description.lower() or "risk" in task_description.lower():
            return await self._threat_modeling(state, handoff)
        else:
            return await self._general_security_analysis(state, handoff)
    
    async def _query_caf_knowledge(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Query CAF knowledge base for assessment checklist"""
        # Query RAG for CAF assessment checklist
        caf_query = "Azure Cloud Adoption Framework security assessment checklist for migration readiness"
        rag_context = await self.query_rag(caf_query, {
            "phase": "assessment",
            "tenant_id": state.get("tenant_id")
        })
        
        prompt = self.format_prompt(
            "Query CAF knowledge base and generate assessment checklist for security domains",
            handoff,
            rag_context
        )
        
        result = await self.call_model(prompt, {
            "findings": state.get("findings", []),
            "phase": state.get("phase")
        })
        
        # Extract assessment domains from response
        checklist_text = result.get("content", "")
        
        # Add finding
        finding = {
            "id": f"finding_{len(state.get('findings', [])) + 1}",
            "domain": "Governance",
            "type": "assessment_checklist",
            "description": "CAF assessment checklist generated",
            "details": checklist_text,
            "agent": self.agent_id,
            "timestamp": state.get("updated_at").isoformat() if hasattr(state.get("updated_at"), "isoformat") else str(state.get("updated_at"))
        }
        state["findings"].append(finding)
        
        # Add event
        state = self.add_event(
            state,
            "Governance",
            "CAF Knowledge Query",
            80.0,
            "Generated CAF assessment checklist"
        )
        
        # Update agent context
        state = self.update_agent_context(
            state,
            task="caf_query",
            artifact={"checklist": checklist_text}
        )
        
        return state
    
    async def _design_architecture(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Design Azure Landing Zone architecture"""
        # Query RAG for CAF Landing Zone guidance
        caf_query = "Azure Landing Zone architecture design Zero Trust security model"
        rag_context = await self.query_rag(caf_query, {
            "findings": state.get("findings", [])
        })
        
        prompt = self.format_prompt(
            "Design Azure Landing Zone architecture based on assessment findings, following CAF principles and Zero Trust model",
            handoff,
            rag_context
        )
        
        prompt += f"\n\nAssessment Findings: {len(state.get('findings', []))} findings identified"
        prompt += "\nDesign must include:"
        prompt += "\n- Hub-and-Spoke network topology"
        prompt += "\n- Identity and Access Management"
        prompt += "\n- Data Protection"
        prompt += "\n- Network Security"
        prompt += "\n- Governance and Compliance"
        prompt += "\n- Monitoring and Logging"
        
        result = await self.call_model(prompt, {
            "findings": state.get("findings", []),
            "critical_risks": state.get("critical_risks", [])
        })
        
        architecture_text = result.get("content", "")
        
        # Store architecture design
        state["architectural_designs"]["landing_zone"] = {
            "description": architecture_text,
            "agent": self.agent_id,
            "timestamp": state.get("updated_at").isoformat() if hasattr(state.get("updated_at"), "isoformat") else str(state.get("updated_at"))
        }
        
        # Add event
        state = self.add_event(
            state,
            "Governance",
            "Architecture Design",
            95.0,
            "Designed Azure Landing Zone architecture"
        )
        
        # Update agent context
        state = self.update_agent_context(
            state,
            task="architecture_design",
            artifact={"architecture": architecture_text}
        )
        
        return state
    
    async def _threat_modeling(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Conduct threat modeling"""
        prompt = self.format_prompt(
            "Conduct threat modeling for the legacy CSP environment and identify security risks",
            handoff
        )
        
        result = await self.call_model(prompt, {
            "findings": state.get("findings", [])
        })
        
        threat_analysis = result.get("content", "")
        
        # Add to critical risks
        risk = {
            "id": f"risk_{len(state.get('critical_risks', [])) + 1}",
            "type": "threat_modeling",
            "description": threat_analysis[:200],
            "agent": self.agent_id
        }
        state["critical_risks"].append(risk)
        
        state = self.add_event(
            state,
            "Governance",
            "Threat Modeling",
            90.0,
            "Completed threat modeling analysis"
        )
        
        return state
    
    async def _general_security_analysis(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """General security analysis"""
        prompt = self.format_prompt(
            "Analyze security posture and provide recommendations",
            handoff
        )
        
        result = await self.call_model(prompt, {
            "findings": state.get("findings", [])
        })
        
        state = self.add_event(
            state,
            "Governance",
            "Security Analysis",
            75.0,
            "Security analysis completed"
        )
        
        return state

