"""
LangGraph State Graph Definition

Main graph structure for multi-agent orchestration.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import AssessmentState, AgentID
from .supervisor import Supervisor
from .langgraph_config import LangGraphConfig


class MultiAgentGraph:
    """
    Main graph for multi-agent orchestration.
    """
    
    def __init__(
        self,
        config: LangGraphConfig,
        supervisor: Supervisor
    ):
        """
        Initialize MultiAgentGraph.
        
        Args:
            config: LangGraphConfig instance
            supervisor: Supervisor instance for routing
        """
        self.config = config
        self.supervisor = supervisor
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph state graph"""
        # Create the graph
        workflow = StateGraph(AssessmentState)
        
        # Add supervisor node
        workflow.add_node("supervisor", self._supervisor_node)
        
        # Add agent nodes
        for agent_id in AgentID:
            if agent_id != AgentID.SUPERVISOR:
                workflow.add_node(
                    agent_id.value,
                    self._create_agent_node(agent_id.value)
                )
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add conditional routing from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self._route_from_supervisor,
            {
                agent_id.value: agent_id.value
                for agent_id in AgentID
                if agent_id != AgentID.SUPERVISOR
            }
        )
        
        # Add edges from agents back to supervisor
        for agent_id in AgentID:
            if agent_id != AgentID.SUPERVISOR:
                workflow.add_edge(agent_id.value, "supervisor")
        
        # Add conditional edge for termination
        workflow.add_conditional_edges(
            "supervisor",
            self._should_terminate,
            {
                "continue": "supervisor",
                "end": END
            }
        )
        
        # Compile with memory checkpointing
        memory = MemorySaver()
        self.graph = workflow.compile(checkpointer=memory)
    
    def _supervisor_node(self, state: AssessmentState) -> AssessmentState:
        """Supervisor node that routes tasks"""
        return self.supervisor.route(state)
    
    def _create_agent_node(self, agent_id: str):
        """Create an agent node function"""
        # Import agents dynamically
        from .agents import (
            MarcusSterling, ElenaBridges, ArisThorne, LeoVance,
            PriyaDesai, RaviPatel, KenjiSato
        )
        
        # Map agent IDs to agent classes
        agent_classes = {
            "marcus_sterling": MarcusSterling,
            "elena_bridges": ElenaBridges,
            "aris_thorne": ArisThorne,
            "leo_vance": LeoVance,
            "priya_desai": PriyaDesai,
            "ravi_patel": RaviPatel,
            "kenji_sato": KenjiSato
        }
        
        agent_class = agent_classes.get(agent_id)
        if not agent_class:
            # Unknown agent, return state unchanged
            async def agent_node(state: AssessmentState) -> AssessmentState:
                return state
            return agent_node
        
        # Create agent instance
        agent = agent_class(
            model_layer=self.config.model_layer,
            state_manager=self.config.state_manager,
            rag_retriever=self.config.rag_retriever
        )
        
        async def agent_node(state: AssessmentState) -> AssessmentState:
            """
            Agent node that processes tasks for a specific agent.
            """
            # Check if this agent should process
            if state.get("current_agent") != agent_id:
                return state
            
            # Get pending handoff for this agent
            handoff = None
            for h in state.get("pending_handoffs", []):
                if h.to_agent == agent_id:
                    handoff = h
                    # Move to completed handoffs
                    state["pending_handoffs"].remove(h)
                    state["completed_handoffs"].append(h)
                    break
            
            # Process the task
            updated_state = await agent.process_task(state, handoff)
            
            return updated_state
        
        return agent_node
    
    def _route_from_supervisor(self, state: AssessmentState) -> str:
        """
        Route from supervisor to appropriate agent.
        
        Returns:
            Agent ID to route to, or "supervisor" to continue routing
        """
        current_agent = state.get("current_agent")
        if current_agent:
            return current_agent
        
        # No agent selected, continue supervisor routing
        return "supervisor"
    
    def _should_terminate(self, state: AssessmentState) -> str:
        """
        Determine if workflow should terminate.
        
        Returns:
            "end" if should terminate, "continue" otherwise
        """
        if state.get("is_complete", False):
            return "end"
        
        from .state import AssessmentPhase
        if state.get("phase") == AssessmentPhase.COMPLETED:
            return "end"
        
        return "continue"
    
    async def run(self, initial_state: AssessmentState, config: Dict[str, Any] = None):
        """
        Run the graph with initial state.
        
        Args:
            initial_state: Initial assessment state
            config: Runtime configuration (thread_id, etc.)
            
        Returns:
            Final state after execution
        """
        if config is None:
            config = {}
        
        # Ensure thread_id for checkpointing
        if "configurable" not in config:
            config["configurable"] = {}
        
        if "thread_id" not in config["configurable"]:
            config["configurable"]["thread_id"] = initial_state["assessment_id"]
        
        # Run the graph
        final_state = None
        async for state in self.graph.astream(initial_state, config=config):
            final_state = state
        
        return final_state

