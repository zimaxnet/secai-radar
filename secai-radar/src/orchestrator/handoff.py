"""
Handoff Pattern Implementation

Implements the handoff pattern for efficient context management and token reduction.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from .state import AssessmentState, HandoffPacket, AgentContext, StateManager


class HandoffManager:
    """
    Manages agent handoffs with context summarization.
    
    Implements the handoff pattern to reduce token usage by:
    - Summarizing context instead of passing full conversation history
    - Creating focused transfer packets
    - Scoping context to only what's needed
    """
    
    def __init__(self, state_manager: StateManager, model_layer=None):
        """
        Initialize HandoffManager.
        
        Args:
            state_manager: StateManager instance
            model_layer: Model Layer for context summarization
        """
        self.state_manager = state_manager
        self.model_layer = model_layer
    
    async def create_handoff(
        self,
        state: AssessmentState,
        from_agent: str,
        to_agent: str,
        task_description: str,
        include_artifacts: Optional[List[str]] = None
    ) -> HandoffPacket:
        """
        Create a handoff packet with summarized context.
        
        Args:
            state: Current assessment state
            from_agent: Source agent ID
            to_agent: Target agent ID
            task_description: Task being handed off
            include_artifacts: List of artifact IDs to include
            
        Returns:
            HandoffPacket with summarized context
        """
        # Get source agent context
        from_context = state.get("agent_contexts", {}).get(from_agent)
        
        # Summarize context
        context_summary = await self._summarize_context(
            state,
            from_agent,
            task_description,
            include_artifacts
        )
        
        # Get required artifacts
        required_artifacts = []
        if include_artifacts and from_context:
            for artifact_id in include_artifacts:
                if artifact_id in from_context.artifacts:
                    required_artifacts.append(artifact_id)
        
        # Create constraints based on state
        constraints = {
            "phase": str(state.get("phase")),
            "budget_remaining": state.get("budget_remaining", 0),
            "critical_risks_count": len(state.get("critical_risks", []))
        }
        
        # Create handoff packet
        handoff = self.state_manager.create_handoff_packet(
            from_agent=from_agent,
            to_agent=to_agent,
            task_description=task_description,
            context_summary=context_summary,
            required_artifacts=required_artifacts,
            constraints=constraints
        )
        
        return handoff
    
    async def _summarize_context(
        self,
        state: AssessmentState,
        agent_id: str,
        task_description: str,
        include_artifacts: Optional[List[str]] = None
    ) -> str:
        """
        Summarize agent context for handoff.
        
        This reduces token usage by creating a concise summary instead of
        passing full conversation history.
        
        Args:
            state: Current assessment state
            agent_id: Agent whose context to summarize
            task_description: Task being handed off
            include_artifacts: Artifacts to include in summary
            
        Returns:
            Summarized context string
        """
        agent_context = state.get("agent_contexts", {}).get(agent_id)
        
        if not agent_context:
            return f"Agent {agent_id} has no previous context."
        
        # Build context summary
        summary_parts = []
        
        # Current task
        if agent_context.current_task:
            summary_parts.append(f"Current task: {agent_context.current_task}")
        
        # Completed tasks (summarized)
        if agent_context.completed_tasks:
            completed_count = len(agent_context.completed_tasks)
            recent_tasks = agent_context.completed_tasks[-3:]  # Last 3 tasks
            summary_parts.append(
                f"Completed {completed_count} tasks. Recent: {', '.join(recent_tasks)}"
            )
        
        # Relevant artifacts
        if include_artifacts and agent_context.artifacts:
            artifact_summaries = []
            for artifact_id in include_artifacts:
                if artifact_id in agent_context.artifacts:
                    artifact = agent_context.artifacts[artifact_id]
                    # Summarize artifact (first 200 chars)
                    artifact_summary = str(artifact)[:200]
                    artifact_summaries.append(f"{artifact_id}: {artifact_summary}...")
            
            if artifact_summaries:
                summary_parts.append("Relevant artifacts:\n" + "\n".join(artifact_summaries))
        
        # Global state summary
        summary_parts.append(f"Assessment phase: {state.get('phase')}")
        summary_parts.append(f"Findings: {len(state.get('findings', []))} identified")
        summary_parts.append(f"Critical risks: {len(state.get('critical_risks', []))}")
        
        # Use model to create concise summary if available
        if self.model_layer and len(summary_parts) > 3:
            full_context = "\n".join(summary_parts)
            prompt = f"""
            Summarize the following context for a handoff to another agent.
            Keep it concise (under 300 words) and focused on what's needed for: {task_description}
            
            Context:
            {full_context}
            
            Provide a concise summary.
            """
            
            try:
                result = await self.model_layer.reasoning(prompt)
                return result.get("content", full_context)
            except Exception:
                # Fallback to basic summary
                return "\n".join(summary_parts)
        
        return "\n".join(summary_parts)
    
    def apply_handoff(
        self,
        state: AssessmentState,
        handoff: HandoffPacket
    ) -> AssessmentState:
        """
        Apply a handoff packet to the state.
        
        Args:
            state: Current assessment state
            handoff: Handoff packet to apply
            
        Returns:
            Updated state
        """
        # Add handoff to pending handoffs
        if "pending_handoffs" not in state:
            state["pending_handoffs"] = []
        
        state["pending_handoffs"].append(handoff)
        
        # Update current agent
        state["current_agent"] = handoff.to_agent
        
        # Update state timestamp
        state["updated_at"] = datetime.utcnow()
        
        return state
    
    def complete_handoff(
        self,
        state: AssessmentState,
        handoff: HandoffPacket
    ) -> AssessmentState:
        """
        Mark a handoff as completed.
        
        Args:
            state: Current assessment state
            handoff: Handoff packet to mark as completed
            
        Returns:
            Updated state
        """
        # Remove from pending
        if handoff in state.get("pending_handoffs", []):
            state["pending_handoffs"].remove(handoff)
        
        # Add to completed
        if "completed_handoffs" not in state:
            state["completed_handoffs"] = []
        
        state["completed_handoffs"].append(handoff)
        
        return state

