"""
Event Emission for Visualization

Structured event emission for real-time visualization in SecAI Radar.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from .state import AssessmentState


class EventType(str, Enum):
    """Event types for visualization"""
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    FINDING_IDENTIFIED = "finding_identified"
    RISK_IDENTIFIED = "risk_identified"
    CONFLICT_DETECTED = "conflict_detected"
    CONFLICT_RESOLVED = "conflict_resolved"
    PHASE_TRANSITION = "phase_transition"
    ARTIFACT_CREATED = "artifact_created"
    HANDOFF_OCCURRED = "handoff_occurred"


class EventEmitter:
    """
    Emits structured events for visualization.
    """
    
    @staticmethod
    def emit_event(
        state: AssessmentState,
        event_type: EventType,
        agent_id: str,
        domain: str,
        action: str,
        impact_score: float,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AssessmentState:
        """
        Emit an event to the state for visualization.
        
        Args:
            state: Current assessment state
            event_type: Type of event
            agent_id: Agent that generated the event
            domain: Security domain
            action: Action taken
            impact_score: Impact score (0-100)
            description: Event description
            metadata: Additional event metadata
            
        Returns:
            Updated state with event added
        """
        event = {
            "id": f"event_{len(state.get('events', [])) + 1}",
            "type": event_type.value,
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "domain": domain,
            "action": action,
            "impact_score": impact_score,
            "description": description,
            "metadata": metadata or {}
        }
        
        if "events" not in state:
            state["events"] = []
        
        state["events"].append(event)
        state["updated_at"] = datetime.utcnow()
        
        return state
    
    @staticmethod
    def get_events_by_domain(
        state: AssessmentState,
        domain: str
    ) -> List[Dict[str, Any]]:
        """
        Get events filtered by domain.
        
        Args:
            state: Assessment state
            domain: Domain to filter by
            
        Returns:
            List of events for the domain
        """
        events = state.get("events", [])
        return [e for e in events if e.get("domain") == domain]
    
    @staticmethod
    def get_recent_events(
        state: AssessmentState,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get most recent events.
        
        Args:
            state: Assessment state
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        events = state.get("events", [])
        # Sort by timestamp (most recent first)
        sorted_events = sorted(
            events,
            key=lambda e: e.get("timestamp", ""),
            reverse=True
        )
        return sorted_events[:limit]

