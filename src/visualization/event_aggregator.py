"""
Event Aggregator

Aggregates and processes events for visualization.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ..orchestrator.state import AssessmentState


class EventAggregator:
    """
    Aggregates events for visualization and analysis.
    """
    
    def __init__(self):
        """Initialize EventAggregator"""
        pass
    
    def aggregate_by_domain(
        self,
        state: AssessmentState
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Aggregate events by security domain.
        
        Args:
            state: Assessment state
            
        Returns:
            Dictionary mapping domains to event lists
        """
        events = state.get("events", [])
        
        domain_events = {}
        for event in events:
            domain = event.get("domain", "Unknown")
            if domain not in domain_events:
                domain_events[domain] = []
            domain_events[domain].append(event)
        
        return domain_events
    
    def aggregate_by_agent(
        self,
        state: AssessmentState
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Aggregate events by agent.
        
        Args:
            state: Assessment state
            
        Returns:
            Dictionary mapping agent IDs to event lists
        """
        events = state.get("events", [])
        
        agent_events = {}
        for event in events:
            agent_id = event.get("agent_id", "unknown")
            if agent_id not in agent_events:
                agent_events[agent_id] = []
            agent_events[agent_id].append(event)
        
        return agent_events
    
    def get_timeline(
        self,
        state: AssessmentState,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get events within a time window.
        
        Args:
            state: Assessment state
            hours: Number of hours to look back
            
        Returns:
            List of events within the time window
        """
        events = state.get("events", [])
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        timeline_events = []
        for event in events:
            event_time_str = event.get("timestamp", "")
            try:
                event_time = datetime.fromisoformat(event_time_str.replace("Z", "+00:00"))
                if event_time >= cutoff_time:
                    timeline_events.append(event)
            except Exception:
                # If timestamp parsing fails, include the event
                timeline_events.append(event)
        
        # Sort by timestamp
        timeline_events.sort(
            key=lambda e: e.get("timestamp", ""),
            reverse=True
        )
        
        return timeline_events
    
    def calculate_metrics(
        self,
        state: AssessmentState
    ) -> Dict[str, Any]:
        """
        Calculate metrics from events.
        
        Args:
            state: Assessment state
            
        Returns:
            Dictionary with calculated metrics
        """
        events = state.get("events", [])
        findings = state.get("findings", [])
        
        total_events = len(events)
        total_findings = len(findings)
        
        # Average impact score
        impact_scores = [e.get("impact_score", 0) for e in events]
        avg_impact = sum(impact_scores) / len(impact_scores) if impact_scores else 0
        
        # Events by type
        event_types = {}
        for event in events:
            event_type = event.get("type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # Critical findings count
        critical_findings = len([
            f for f in findings
            if f.get("severity") == "critical"
        ])
        
        return {
            "total_events": total_events,
            "total_findings": total_findings,
            "critical_findings": critical_findings,
            "average_impact_score": avg_impact,
            "events_by_type": event_types,
            "phase": str(state.get("phase")),
            "budget_remaining": state.get("budget_remaining", 0)
        }

