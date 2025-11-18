"""
Base Agent Class

Base class for all agent personas with common functionality.
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from datetime import datetime

from ..state import AssessmentState, HandoffPacket, AgentContext, StateManager


class BaseAgent(ABC):
    """
    Base class for all agent personas.
    Provides common functionality for agent operations.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        system_prompt: str,
        model_layer=None,
        state_manager: Optional[StateManager] = None,
        rag_retriever=None,
        tools: Optional[List[str]] = None
    ):
        """
        Initialize base agent.
        
        Args:
            agent_id: Unique agent identifier
            name: Agent name
            role: Agent role/title
            system_prompt: System prompt for this agent
            model_layer: Model Layer instance for LLM access
            state_manager: StateManager instance
            rag_retriever: RAG retriever for knowledge base queries
            tools: List of tool names available to this agent
        """
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model_layer = model_layer
        self.state_manager = state_manager or StateManager()
        self.rag_retriever = rag_retriever
        self.tools = tools or []
    
    @abstractmethod
    async def process_task(
        self,
        state: AssessmentState,
        handoff: Optional[HandoffPacket] = None
    ) -> AssessmentState:
        """
        Process a task assigned to this agent.
        
        Args:
            state: Current assessment state
            handoff: Handoff packet with task details (if any)
            
        Returns:
            Updated state after processing
        """
        pass
    
    async def query_rag(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Query the RAG knowledge base.
        
        Args:
            query: Search query
            context: Additional context for the query
            
        Returns:
            Retrieved context or None
        """
        if not self.rag_retriever:
            return None
        
        try:
            result = await self.rag_retriever.retrieve(query, context)
            return result
        except Exception as e:
            print(f"Error querying RAG: {e}")
            return None
    
    async def call_model(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        model_role: str = "reasoning_model"
    ) -> Dict[str, Any]:
        """
        Call the model layer with a prompt.
        
        Args:
            prompt: User prompt
            context: Additional context
            model_role: Model role to use (reasoning, classification, generation)
            
        Returns:
            Model response
        """
        if not self.model_layer:
            return {"content": "Model layer not available", "error": True}
        
        try:
            if model_role == "reasoning_model":
                result = await self.model_layer.reasoning(prompt, context)
            elif model_role == "classification_model":
                result = await self.model_layer.classify(context or {})
            elif model_role == "generation_model":
                result = await self.model_layer.generate(
                    section_type=prompt,
                    data=context or {}
                )
            else:
                result = await self.model_layer.reasoning(prompt, context)
            
            return result
        except Exception as e:
            print(f"Error calling model: {e}")
            return {"content": f"Error: {e}", "error": True}
    
    def update_agent_context(
        self,
        state: AssessmentState,
        task: Optional[str] = None,
        artifact: Optional[Dict[str, Any]] = None
    ) -> AssessmentState:
        """
        Update this agent's context in the state.
        
        Args:
            state: Current state
            task: Task to record
            artifact: Artifact to store
            
        Returns:
            Updated state
        """
        return self.state_manager.update_agent_context(
            state,
            self.agent_id,
            task,
            artifact
        )
    
    def add_event(
        self,
        state: AssessmentState,
        domain: str,
        action: str,
        impact_score: float,
        description: str
    ) -> AssessmentState:
        """
        Add an event to the state for visualization.
        
        Args:
            state: Current state
            domain: Security domain
            action: Action taken
            impact_score: Impact score (0-100)
            description: Event description
            
        Returns:
            Updated state
        """
        return self.state_manager.add_event(
            state,
            self.agent_id,
            domain,
            action,
            impact_score,
            description
        )
    
    def create_handoff(
        self,
        to_agent: str,
        task_description: str,
        context_summary: str,
        required_artifacts: Optional[List[str]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> HandoffPacket:
        """
        Create a handoff packet to another agent.
        
        Args:
            to_agent: Target agent ID
            task_description: Description of the task
            context_summary: Summarized context
            required_artifacts: Required artifact IDs
            constraints: Constraints or requirements
            
        Returns:
            HandoffPacket instance
        """
        return self.state_manager.create_handoff_packet(
            from_agent=self.agent_id,
            to_agent=to_agent,
            task_description=task_description,
            context_summary=context_summary,
            required_artifacts=required_artifacts,
            constraints=constraints
        )
    
    def get_agent_context(self, state: AssessmentState) -> Optional[AgentContext]:
        """
        Get this agent's context from state.
        
        Args:
            state: Current state
            
        Returns:
            AgentContext or None
        """
        return state.get("agent_contexts", {}).get(self.agent_id)
    
    def format_prompt(
        self,
        task_description: str,
        handoff: Optional[HandoffPacket] = None,
        rag_context: Optional[str] = None
    ) -> str:
        """
        Format a prompt for the agent with context.
        
        Args:
            task_description: Task to perform
            handoff: Handoff packet (if any)
            rag_context: RAG-retrieved context (if any)
            
        Returns:
            Formatted prompt
        """
        prompt_parts = [f"Task: {task_description}"]
        
        if handoff:
            prompt_parts.append(f"\nContext from {handoff.from_agent}:")
            prompt_parts.append(handoff.context_summary)
            
            if handoff.constraints:
                prompt_parts.append("\nConstraints:")
                for key, value in handoff.constraints.items():
                    prompt_parts.append(f"- {key}: {value}")
        
        if rag_context:
            prompt_parts.append("\nRelevant Knowledge Base Information:")
            prompt_parts.append(rag_context)
        
        return "\n".join(prompt_parts)

