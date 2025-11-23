"""
State Management for Multi-Agent Orchestration

Defines the global state schema and handoff packet structure for agent communication.
Implements the handoff pattern to reduce token usage and manage context efficiently.
"""

from typing import Dict, List, Optional, Any, TypedDict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AssessmentPhase(str, Enum):
    """Assessment workflow phases"""
    ASSESSMENT = "assessment"
    DESIGN = "design"
    MIGRATION = "migration"
    COMPLETED = "completed"


class AgentID(str, Enum):
    """Agent identifiers"""
    MARCUS_STERLING = "marcus_sterling"
    ELENA_BRIDGES = "elena_bridges"
    ARIS_THORNE = "aris_thorne"
    LEO_VANCE = "leo_vance"
    PRIYA_DESAI = "priya_desai"
    RAVI_PATEL = "ravi_patel"
    KENJI_SATO = "kenji_sato"
    SUPERVISOR = "supervisor"


@dataclass
class HandoffPacket:
    """
    Transfer packet for agent handoffs.
    Contains only the essential context needed for the receiving agent.
    """
    from_agent: str
    to_agent: str
    task_description: str
    context_summary: str
    required_artifacts: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgentContext:
    """Agent-specific context and state"""
    agent_id: str
    current_task: Optional[str] = None
    completed_tasks: List[str] = field(default_factory=list)
    pending_tasks: List[str] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class AssessmentState(TypedDict):
    """
    Global state for the assessment workflow.
    This is the state object passed between LangGraph nodes.
    """
    # Assessment metadata
    assessment_id: str
    tenant_id: str
    phase: AssessmentPhase
    created_at: datetime
    updated_at: datetime
    
    # Project management
    budget: float
    budget_remaining: float
    critical_risks: List[Dict[str, Any]]
    timeline: Dict[str, Any]
    
    # Agent contexts
    agent_contexts: Dict[str, AgentContext]
    
    # Workflow state
    current_agent: Optional[str]
    pending_handoffs: List[HandoffPacket]
    completed_handoffs: List[HandoffPacket]
    
    # Findings and artifacts
    findings: List[Dict[str, Any]]
    architectural_designs: Dict[str, Any]
    migration_plan: Optional[Dict[str, Any]]
    
    # Conflict resolution
    active_conflicts: List[Dict[str, Any]]
    resolved_conflicts: List[Dict[str, Any]]
    
    # Events for visualization
    events: List[Dict[str, Any]]
    
    # Termination condition
    is_complete: bool
    termination_reason: Optional[str]


class StateManager:
    """
    Manages state persistence and retrieval.
    Handles state updates and handoff packet creation.
    """
    
    def __init__(self, cosmos_client=None, cosmos_persistence=None):
        """
        Initialize StateManager.
        
        Args:
            cosmos_client: Azure Cosmos DB client (legacy, optional)
            cosmos_persistence: CosmosStatePersistence instance (preferred)
        """
        self.cosmos_client = cosmos_client
        self.cosmos_persistence = cosmos_persistence
    
    def create_initial_state(
        self,
        assessment_id: str,
        tenant_id: str,
        budget: float = 100000.0
    ) -> AssessmentState:
        """
        Create initial assessment state.
        
        Args:
            assessment_id: Unique assessment identifier
            tenant_id: Tenant identifier
            budget: Initial budget
            
        Returns:
            Initialized AssessmentState
        """
        now = datetime.utcnow()
        
        # Initialize agent contexts
        agent_contexts = {
            agent_id.value: AgentContext(agent_id=agent_id.value)
            for agent_id in AgentID
            if agent_id != AgentID.SUPERVISOR
        }
        
        return AssessmentState(
            assessment_id=assessment_id,
            tenant_id=tenant_id,
            phase=AssessmentPhase.ASSESSMENT,
            created_at=now,
            updated_at=now,
            budget=budget,
            budget_remaining=budget,
            critical_risks=[],
            timeline={},
            agent_contexts=agent_contexts,
            current_agent=None,
            pending_handoffs=[],
            completed_handoffs=[],
            findings=[],
            architectural_designs={},
            migration_plan=None,
            active_conflicts=[],
            resolved_conflicts=[],
            events=[],
            is_complete=False,
            termination_reason=None
        )
    
    def create_handoff_packet(
        self,
        from_agent: str,
        to_agent: str,
        task_description: str,
        context_summary: str,
        required_artifacts: Optional[List[str]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> HandoffPacket:
        """
        Create a handoff packet for agent-to-agent communication.
        
        This implements the handoff pattern to reduce token usage by
        summarizing context instead of passing full conversation history.
        
        Args:
            from_agent: Source agent ID
            to_agent: Target agent ID
            task_description: Description of the task being handed off
            context_summary: Summarized context (not full history)
            required_artifacts: List of artifact IDs needed
            constraints: Any constraints or requirements
            
        Returns:
            HandoffPacket instance
        """
        return HandoffPacket(
            from_agent=from_agent,
            to_agent=to_agent,
            task_description=task_description,
            context_summary=context_summary,
            required_artifacts=required_artifacts or [],
            constraints=constraints or {}
        )
    
    def update_agent_context(
        self,
        state: AssessmentState,
        agent_id: str,
        task: Optional[str] = None,
        artifact: Optional[Dict[str, Any]] = None
    ) -> AssessmentState:
        """
        Update agent-specific context in state.
        
        Args:
            state: Current assessment state
            agent_id: Agent identifier
            task: Current or completed task
            artifact: Artifact to store
            
        Returns:
            Updated state
        """
        if agent_id not in state["agent_contexts"]:
            state["agent_contexts"][agent_id] = AgentContext(agent_id=agent_id)
        
        agent_ctx = state["agent_contexts"][agent_id]
        
        if task:
            if agent_ctx.current_task:
                agent_ctx.completed_tasks.append(agent_ctx.current_task)
            agent_ctx.current_task = task
        
        if artifact:
            artifact_id = artifact.get("id", f"artifact_{len(agent_ctx.artifacts)}")
            agent_ctx.artifacts[artifact_id] = artifact
        
        agent_ctx.last_updated = datetime.utcnow()
        state["updated_at"] = datetime.utcnow()
        
        return state
    
    def add_event(
        self,
        state: AssessmentState,
        agent_id: str,
        domain: str,
        action: str,
        impact_score: float,
        description: str
    ) -> AssessmentState:
        """
        Add an event to the state for visualization.
        
        Args:
            state: Current assessment state
            agent_id: Agent that generated the event
            domain: Security domain (Identity, Network, etc.)
            action: Action taken
            impact_score: Impact score (0-100)
            description: Event description
            
        Returns:
            Updated state
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "domain": domain,
            "action": action,
            "impact_score": impact_score,
            "description": description
        }
        
        state["events"].append(event)
        state["updated_at"] = datetime.utcnow()
        
        return state
    
    async def persist_state(self, state: AssessmentState) -> bool:
        """
        Persist state to Cosmos DB.
        
        Args:
            state: Assessment state to persist
            
        Returns:
            True if successful
        """
        # Use new CosmosStatePersistence if available
        if self.cosmos_persistence:
            import asyncio
            # Cosmos DB SDK is synchronous, run in thread pool
            return await asyncio.to_thread(
                self.cosmos_persistence.persist_state,
                state,
                self
            )
        
        # Fallback to legacy cosmos_client if provided
        if not self.cosmos_client:
            # No persistence configured, skip
            return True
        
        try:
            # Convert state to dict for Cosmos DB
            state_dict = self._state_to_dict(state)
            
            # Upsert to Cosmos DB
            container = self.cosmos_client.get_database_client(
                "secai_radar"
            ).get_container_client("assessment_states")
            
            await container.upsert_item(state_dict)
            return True
        except Exception as e:
            print(f"Error persisting state: {e}")
            return False
    
    async def load_state(self, assessment_id: str) -> Optional[AssessmentState]:
        """
        Load state from Cosmos DB.
        
        Args:
            assessment_id: Assessment identifier
            
        Returns:
            AssessmentState if found, None otherwise
        """
        # Use new CosmosStatePersistence if available
        if self.cosmos_persistence:
            import asyncio
            # Cosmos DB SDK is synchronous, run in thread pool
            return await asyncio.to_thread(
                self.cosmos_persistence.load_state,
                assessment_id,
                self
            )
        
        # Fallback to legacy cosmos_client if provided
        if not self.cosmos_client:
            return None
        
        try:
            container = self.cosmos_client.get_database_client(
                "secai_radar"
            ).get_container_client("assessment_states")
            
            item = await container.read_item(assessment_id, assessment_id)
            return self._dict_to_state(item)
        except Exception as e:
            print(f"Error loading state: {e}")
            return None
    
    def _state_to_dict(self, state: AssessmentState) -> Dict[str, Any]:
        """Convert AssessmentState to dictionary for persistence"""
        # Convert TypedDict to regular dict
        result = dict(state)
        
        # Convert enums to strings
        result["phase"] = state["phase"].value if isinstance(state["phase"], AssessmentPhase) else state["phase"]
        
        # Convert datetimes to ISO strings
        for key in ["created_at", "updated_at"]:
            if key in result and isinstance(result[key], datetime):
                result[key] = result[key].isoformat()
        
        # Convert agent contexts
        if "agent_contexts" in result:
            result["agent_contexts"] = {
                k: {
                    "agent_id": v.agent_id,
                    "current_task": v.current_task,
                    "completed_tasks": v.completed_tasks,
                    "pending_tasks": v.pending_tasks,
                    "artifacts": v.artifacts,
                    "last_updated": v.last_updated.isoformat() if isinstance(v.last_updated, datetime) else v.last_updated
                }
                for k, v in result["agent_contexts"].items()
            }
        
        # Convert handoff packets
        for key in ["pending_handoffs", "completed_handoffs"]:
            if key in result:
                result[key] = [
                    {
                        "from_agent": p.from_agent,
                        "to_agent": p.to_agent,
                        "task_description": p.task_description,
                        "context_summary": p.context_summary,
                        "required_artifacts": p.required_artifacts,
                        "constraints": p.constraints,
                        "timestamp": p.timestamp.isoformat() if isinstance(p.timestamp, datetime) else p.timestamp
                    }
                    for p in result[key]
                ]
        
        return result
    
    def _dict_to_state(self, data: Dict[str, Any]) -> AssessmentState:
        """Convert dictionary to AssessmentState"""
        # Convert phase string back to enum
        if "phase" in data and isinstance(data["phase"], str):
            data["phase"] = AssessmentPhase(data["phase"])
        
        # Convert ISO strings back to datetimes
        for key in ["created_at", "updated_at"]:
            if key in data and isinstance(data[key], str):
                data[key] = datetime.fromisoformat(data[key])
        
        # Convert agent contexts back
        if "agent_contexts" in data:
            data["agent_contexts"] = {
                k: AgentContext(
                    agent_id=v["agent_id"],
                    current_task=v.get("current_task"),
                    completed_tasks=v.get("completed_tasks", []),
                    pending_tasks=v.get("pending_tasks", []),
                    artifacts=v.get("artifacts", {}),
                    last_updated=datetime.fromisoformat(v["last_updated"]) if isinstance(v.get("last_updated"), str) else v.get("last_updated", datetime.utcnow())
                )
                for k, v in data["agent_contexts"].items()
            }
        
        # Convert handoff packets back
        for key in ["pending_handoffs", "completed_handoffs"]:
            if key in data:
                data[key] = [
                    HandoffPacket(
                        from_agent=p["from_agent"],
                        to_agent=p["to_agent"],
                        task_description=p["task_description"],
                        context_summary=p["context_summary"],
                        required_artifacts=p.get("required_artifacts", []),
                        constraints=p.get("constraints", {}),
                        timestamp=datetime.fromisoformat(p["timestamp"]) if isinstance(p.get("timestamp"), str) else p.get("timestamp", datetime.utcnow())
                    )
                    for p in data[key]
                ]
        
        return AssessmentState(**data)

