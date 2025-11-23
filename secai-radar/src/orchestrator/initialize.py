"""
Orchestrator Initialization

Helper functions to initialize the multi-agent orchestration system
with all dependencies (Model Layer, RAG, State Management).
"""

import os
from pathlib import Path
from typing import Optional

from .state import StateManager
from .cosmos_persistence import CosmosStatePersistence
from .supervisor import Supervisor
from .langgraph_config import LangGraphConfig
from .graph import MultiAgentGraph

# Import model layer
try:
    from ..models import get_model_layer
except ImportError:
    # Fallback if models not available
    get_model_layer = None

# Import RAG factory
try:
    from ..rag.factory import get_rag_retriever
except ImportError:
    get_rag_retriever = None


def initialize_orchestrator(
    model_layer=None,
    rag_retriever=None,
    cosmos_persistence=None,
    state_manager=None
) -> MultiAgentGraph:
    """
    Initialize the complete multi-agent orchestration system.
    
    This function sets up all dependencies:
    - Model Layer (for agent LLM access)
    - RAG Retriever (for knowledge base queries)
    - State Manager (with Cosmos DB persistence)
    - Supervisor (for routing)
    - LangGraph (for orchestration)
    
    Args:
        model_layer: Model Layer instance (or None to auto-initialize)
        rag_retriever: RAG retriever instance (or None to auto-initialize from config)
        cosmos_persistence: CosmosStatePersistence instance (or None to auto-initialize)
        state_manager: StateManager instance (or None to auto-initialize)
        
    Returns:
        Configured MultiAgentGraph instance
    """
    # Initialize Model Layer if not provided
    if model_layer is None and get_model_layer:
        try:
            model_layer = get_model_layer()
        except Exception as e:
            print(f"Warning: Could not initialize Model Layer: {e}")
            model_layer = None
    
    # Initialize RAG Retriever if not provided
    if rag_retriever is None and get_rag_retriever:
        try:
            rag_retriever = get_rag_retriever(model_layer=model_layer)
            if rag_retriever:
                print("✅ RAG Retriever initialized (Google File Search)")
            else:
                print("⚠️  RAG Retriever not available (check GOOGLE_API_KEY)")
        except Exception as e:
            print(f"Warning: Could not initialize RAG Retriever: {e}")
            rag_retriever = None
    
    # Initialize Cosmos DB Persistence if not provided
    if cosmos_persistence is None:
        cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
        cosmos_key = os.getenv("COSMOS_KEY")
        
        if cosmos_endpoint and cosmos_key:
            try:
                cosmos_persistence = CosmosStatePersistence(
                    cosmos_endpoint=cosmos_endpoint,
                    cosmos_key=cosmos_key
                )
                print("✅ Cosmos DB persistence initialized")
            except Exception as e:
                print(f"Warning: Could not initialize Cosmos DB: {e}")
                cosmos_persistence = None
        else:
            print("⚠️  Cosmos DB not configured (set COSMOS_ENDPOINT and COSMOS_KEY)")
    
    # Initialize State Manager
    if state_manager is None:
        state_manager = StateManager(cosmos_persistence=cosmos_persistence)
    
    # Initialize Supervisor
    supervisor = Supervisor(state_manager, model_layer)
    
    # Initialize LangGraph Config
    config = LangGraphConfig(
        model_layer=model_layer,
        state_manager=state_manager,
        rag_retriever=rag_retriever
    )
    
    # Create and return the graph
    graph = MultiAgentGraph(config, supervisor)
    
    print("✅ Multi-agent orchestration system initialized")
    return graph


def create_example_usage():
    """
    Create an example showing how to use the orchestrator.
    
    Returns:
        Example code as string
    """
    return """
# Example: Initialize and run multi-agent assessment

from src.orchestrator.initialize import initialize_orchestrator
from src.orchestrator.state import StateManager

# Initialize orchestrator (auto-configures from environment)
graph = initialize_orchestrator()

# Create initial state
state_manager = StateManager()
initial_state = state_manager.create_initial_state(
    assessment_id="assessment-001",
    tenant_id="tenant-alpha",
    budget=100000.0
)

# Run the assessment workflow
final_state = await graph.run(initial_state)

# Access results
print(f"Phase: {final_state['phase']}")
print(f"Findings: {len(final_state['findings'])}")
print(f"Events: {len(final_state['events'])}")
"""

