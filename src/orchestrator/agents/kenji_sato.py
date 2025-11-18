"""
Kenji Sato - Program Manager Agent

Schedule tracking, status reporting, and dependency management.
"""

from typing import Dict, Any, Optional
from ..state import AssessmentState, HandoffPacket, AgentID
from .base_agent import BaseAgent


class KenjiSato(BaseAgent):
    """
    Kenji Sato - Program Manager focused on schedule and status tracking.
    """
    
    def __init__(self, model_layer=None, state_manager=None, rag_retriever=None):
        """Initialize Kenji Sato agent"""
        super().__init__(
            agent_id=AgentID.KENJI_SATO.value,
            name="Kenji Sato",
            role="Program Manager",
            system_prompt="""You are Kenji Sato, a Program Manager.
            You track schedules, dependencies, and generate status reports.
            Maintain accurate timelines and identify risks early.""",
            model_layer=model_layer,
            state_manager=state_manager,
            rag_retriever=rag_retriever,
            tools=["update_schedule", "generate_status_report", "track_dependencies", "identify_risks"]
        )
    
    async def process_task(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket] = None
    ) -> AssessmentState:
        """
        Process schedule tracking or status reporting task.
        
        Args:
            state: Current assessment state
            handoff: Handoff packet with task details
            
        Returns:
            Updated state
        """
        task_description = handoff.task_description if handoff else "Track project status"
        
        if "collate" in task_description.lower() or "findings" in task_description.lower() or "status" in task_description.lower():
            return await self._collate_findings(state, handoff)
        elif "schedule" in task_description.lower() or "timeline" in task_description.lower():
            return await self._update_schedule(state, handoff)
        elif "dependency" in task_description.lower():
            return await self._track_dependencies(state, handoff)
        else:
            return await self._generate_status_report(state, handoff)
    
    async def _collate_findings(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Collate assessment findings into status report"""
        findings = state.get("findings", [])
        
        prompt = self.format_prompt(
            "Collate all assessment findings into a comprehensive status report. "
            "Organize by domain and provide summary statistics.",
            handoff
        )
        
        prompt += f"\n\nFindings to collate: {len(findings)} findings"
        prompt += "\n\nOrganize by:"
        prompt += "\n- Security Domain"
        prompt += "\n- Severity"
        prompt += "\n- Agent responsible"
        prompt += "\n- Status"
        
        result = await self.call_model(prompt, {
            "findings": findings
        })
        
        status_report = result.get("content", "")
        
        # Store status report
        state["timeline"]["status_report"] = {
            "description": status_report,
            "agent": self.agent_id,
            "timestamp": state.get("updated_at").isoformat() if hasattr(state.get("updated_at"), "isoformat") else str(state.get("updated_at"))
        }
        
        # Add event
        state = self.add_event(
            state,
            "Governance",
            "Findings Collation",
            80.0,
            f"Collated {len(findings)} findings into status report"
        )
        
        # Update agent context
        state = self.update_agent_context(
            state,
            task="findings_collation",
            artifact={"status_report": status_report}
        )
        
        return state
    
    async def _update_schedule(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Update project schedule"""
        prompt = self.format_prompt(
            "Update the project schedule and timeline based on current progress",
            handoff
        )
        
        result = await self.call_model(prompt, {
            "phase": state.get("phase"),
            "findings": len(state.get("findings", []))
        })
        
        state = self.add_event(
            state,
            "Governance",
            "Schedule Update",
            70.0,
            "Updated project schedule"
        )
        
        return state
    
    async def _track_dependencies(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Track task dependencies"""
        prompt = self.format_prompt(
            "Identify and track dependencies between tasks. Flag any blocking dependencies.",
            handoff
        )
        
        result = await self.call_model(prompt)
        
        state = self.add_event(
            state,
            "Governance",
            "Dependency Tracking",
            75.0,
            "Tracked task dependencies"
        )
        
        return state
    
    async def _generate_status_report(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket]
    ) -> AssessmentState:
        """Generate status report"""
        prompt = self.format_prompt(
            "Generate daily status report with progress updates and risks",
            handoff
        )
        
        result = await self.call_model(prompt, {
            "phase": state.get("phase"),
            "findings": len(state.get("findings", [])),
            "critical_risks": len(state.get("critical_risks", []))
        })
        
        state = self.add_event(
            state,
            "Governance",
            "Status Report",
            70.0,
            "Generated status report"
        )
        
        return state

