"""
LangGraph Configuration

Configuration and setup for LangGraph multi-agent orchestration.
"""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .state import AssessmentState, StateManager, AgentID


class LangGraphConfig:
    """
    Configuration for LangGraph orchestration.
    """
    
    def __init__(
        self,
        model_layer=None,
        state_manager: Optional[StateManager] = None,
        rag_retriever=None
    ):
        """
        Initialize LangGraph configuration.
        
        Args:
            model_layer: Model Layer instance for agent LLM access
            state_manager: StateManager instance for state persistence
            rag_retriever: RAG retriever for knowledge base queries
        """
        self.model_layer = model_layer
        self.state_manager = state_manager or StateManager()
        self.rag_retriever = rag_retriever
    
    def create_graph(self) -> StateGraph:
        """
        Create the LangGraph state graph for multi-agent orchestration.
        
        Returns:
            Configured StateGraph instance
        """
        # Create the graph
        workflow = StateGraph(AssessmentState)
        
        # Add supervisor node (routing logic)
        workflow.add_node("supervisor", self.supervisor_node)
        
        # Add agent nodes
        for agent_id in AgentID:
            if agent_id != AgentID.SUPERVISOR:
                workflow.add_node(agent_id.value, self.create_agent_node(agent_id.value))
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add edges from supervisor to agents
        for agent_id in AgentID:
            if agent_id != AgentID.SUPERVISOR:
                workflow.add_edge("supervisor", agent_id.value)
        
        # Add edges from agents back to supervisor
        for agent_id in AgentID:
            if agent_id != AgentID.SUPERVISOR:
                workflow.add_edge(agent_id.value, "supervisor")
        
        # Add conditional edge for termination
        workflow.add_conditional_edges(
            "supervisor",
            self.should_continue,
            {
                "continue": "supervisor",
                "end": END
            }
        )
        
        return workflow.compile()
    
    def supervisor_node(self, state: AssessmentState) -> AssessmentState:
        """
        Supervisor node that routes tasks to appropriate agents.
        
        Args:
            state: Current assessment state
            
        Returns:
            Updated state
        """
        # Supervisor routing logic will be implemented in supervisor.py
        # This is a placeholder that returns state unchanged
        # The actual routing will be handled by the Supervisor class
        return state
    
    def create_agent_node(self, agent_id: str):
        """
        Create an agent node function for LangGraph.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Node function that processes agent tasks
        """
        async def agent_node(state: AssessmentState) -> AssessmentState:
            """
            Agent node that processes tasks for a specific agent.
            
            Args:
                state: Current assessment state
                
            Returns:
                Updated state
            """
            # Agent processing will be implemented in agents/
            # This is a placeholder
            return state
        
        return agent_node
    
    def should_continue(self, state: AssessmentState) -> str:
        """
        Determine if the workflow should continue or terminate.
        
        Args:
            state: Current assessment state
            
        Returns:
            "continue" or "end"
        """
        if state.get("is_complete", False):
            return "end"
        
        # Check if phase is completed
        from .state import AssessmentPhase
        if state.get("phase") == AssessmentPhase.COMPLETED:
            return "end"
        
        return "continue"

