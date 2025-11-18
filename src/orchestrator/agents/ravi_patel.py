"""
Ravi Patel - Security Engineer Agent

IaC development, policy implementation, and vulnerability scanning.
"""

from typing import Dict, Any, Optional
from ..state import AssessmentState, HandoffPacket, AgentID
from .base_agent import BaseAgent


class RaviPatel(BaseAgent):
    """
    Ravi Patel - Security Engineer focused on implementation.
    """
    
    def __init__(self, model_layer=None, state_manager=None, rag_retriever=None):
        """Initialize Ravi Patel agent"""
        super().__init__(
            agent_id=AgentID.RAVI_PATEL.value,
            name="Ravi Patel",
            role="Security Engineer",
            system_prompt="""You are Ravi Patel, a Security Engineer.
            You write clean, maintainable Infrastructure as Code (IaC) and implement security policies.
            Focus on practical implementation and working, tested code.""",
            model_layer=model_layer,
            state_manager=state_manager,
            rag_retriever=rag_retriever,
            tools=["generate_terraform", "implement_policy", "run_scan", "validate_iac"]
        )
    
    async def process_task(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket] = None
    ) -> AssessmentState:
        """
        Process implementation task (IaC, policies, scans).
        
        Args:
            state: Current assessment state
            handoff: Handoff packet with task details
            
        Returns:
            Updated state
        """
        task_description = handoff.task_description if handoff else "Implement security controls"
        
        if "scan" in task_description.lower() or "infrastructure" in task_description.lower():
            return await self._run_scan(state, handoff)
        elif "terraform" in task_description.lower() or "bicep" in task_description.lower() or "iac" in task_description.lower():
            return await self._generate_iac(state, handoff)
        elif "policy" in task_description.lower():
            return await self._implement_policy(state, handoff)
        else:
            return await self._general_implementation(state, handoff)
    
    async def _run_scan(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Run infrastructure security scan"""
        prompt = self.format_prompt(
            "Run security scan of legacy CSP networking and infrastructure. "
            "Identify security gaps and vulnerabilities.",
            handoff
        )
        
        result = await self.call_model(prompt, {
            "tenant_id": state.get("tenant_id")
        })
        
        scan_results = result.get("content", "")
        
        # Add finding
        finding = {
            "id": f"finding_{len(state.get('findings', [])) + 1}",
            "domain": "Network Security",
            "type": "infrastructure_scan",
            "description": "Infrastructure security scan completed",
            "details": scan_results,
            "agent": self.agent_id,
            "severity": "critical" if "critical" in scan_results.lower() else "medium"
        }
        state["findings"].append(finding)
        
        # Add event
        state = self.add_event(
            state,
            "Network Security",
            "Infrastructure Scan",
            90.0,
            "Completed infrastructure security scan"
        )
        
        # Update agent context
        state = self.update_agent_context(
            state,
            task="infrastructure_scan",
            artifact={"scan_results": scan_results}
        )
        
        return state
    
    async def _generate_iac(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Generate Infrastructure as Code"""
        # Get architecture design
        architecture = state.get("architectural_designs", {}).get("landing_zone", {})
        
        prompt = self.format_prompt(
            "Generate Terraform or Bicep code to implement the Azure Landing Zone architecture. "
            "Provide working, tested code with proper documentation.",
            handoff
        )
        
        if architecture:
            prompt += f"\n\nArchitecture Design:\n{architecture.get('description', '')[:1000]}"
        
        prompt += "\n\nCode Requirements:"
        prompt += "\n- Clean, maintainable code"
        prompt += "\n- Proper error handling"
        prompt += "\n- Documentation and comments"
        prompt += "\n- Follow Azure best practices"
        
        result = await self.call_model(prompt, {
            "architecture": architecture
        })
        
        iac_code = result.get("content", "")
        
        # Store IaC artifact
        artifact = {
            "id": f"iac_{len(state.get('findings', [])) + 1}",
            "type": "infrastructure_code",
            "code": iac_code,
            "agent": self.agent_id
        }
        
        # Update agent context
        state = self.update_agent_context(
            state,
            task="iac_generation",
            artifact=artifact
        )
        
        # Add event
        state = self.add_event(
            state,
            "Network Security",
            "IaC Generation",
            85.0,
            "Generated Infrastructure as Code"
        )
        
        return state
    
    async def _implement_policy(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Implement Azure Policy definitions"""
        prompt = self.format_prompt(
            "Generate Azure Policy definitions to enforce security controls",
            handoff
        )
        
        result = await self.call_model(prompt)
        
        state = self.add_event(
            state,
            "Governance",
            "Policy Implementation",
            80.0,
            "Implemented Azure Policy definitions"
        )
        
        return state
    
    async def _general_implementation(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """General implementation task"""
        prompt = self.format_prompt(
            "Implement security controls as specified",
            handoff
        )
        
        result = await self.call_model(prompt)
        
        state = self.add_event(
            state,
            "Network Security",
            "Implementation",
            70.0,
            "Completed implementation task"
        )
        
        return state

