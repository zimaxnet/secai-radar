"""
SecAI Radar Chart Generator

Generates radar charts (spider charts) showing security posture across 5 CAF domains.
"""

from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
import plotly.express as px

from ..orchestrator.state import AssessmentState


class RadarChartGenerator:
    """
    Generates radar charts for SecAI Radar visualization.
    
    The radar chart shows security posture across 5 axes:
    - Identity & Access
    - Data Protection
    - Network Security
    - Governance
    - Monitoring
    """
    
    # CAF Security Domains
    DOMAINS = [
        "Identity & Access",
        "Data Protection",
        "Network Security",
        "Governance",
        "Monitoring"
    ]
    
    def __init__(self):
        """Initialize RadarChartGenerator"""
        pass
    
    def calculate_domain_scores(
        self,
        state: AssessmentState
    ) -> Dict[str, float]:
        """
        Calculate security posture scores for each domain based on events and findings.
        
        Args:
            state: Assessment state with events and findings
            
        Returns:
            Dictionary mapping domain names to scores (0-100)
        """
        events = state.get("events", [])
        findings = state.get("findings", [])
        
        domain_scores = {domain: 0.0 for domain in self.DOMAINS}
        domain_weights = {domain: 0 for domain in self.DOMAINS}
        
        # Map domain names to standard domains
        domain_mapping = {
            "Identity": "Identity & Access",
            "Identity & Access": "Identity & Access",
            "Data Protection": "Data Protection",
            "Data": "Data Protection",
            "Network Security": "Network Security",
            "Network": "Network Security",
            "Governance": "Governance",
            "Monitoring": "Monitoring",
            "Logging": "Monitoring"
        }
        
        # Calculate scores from events
        for event in events:
            domain = event.get("domain", "")
            mapped_domain = domain_mapping.get(domain, domain)
            
            if mapped_domain in domain_scores:
                impact_score = event.get("impact_score", 0)
                domain_scores[mapped_domain] += impact_score
                domain_weights[mapped_domain] += 1
        
        # Calculate scores from findings
        for finding in findings:
            domain = finding.get("domain", "")
            mapped_domain = domain_mapping.get(domain, domain)
            
            if mapped_domain in domain_scores:
                # Findings reduce score (negative impact)
                severity = finding.get("severity", "medium")
                severity_multiplier = {
                    "critical": -20,
                    "high": -15,
                    "medium": -10,
                    "low": -5
                }
                impact = severity_multiplier.get(severity, -10)
                domain_scores[mapped_domain] += impact
                domain_weights[mapped_domain] += 1
        
        # Normalize scores (0-100 scale)
        for domain in self.DOMAINS:
            if domain_weights[domain] > 0:
                # Average the scores
                domain_scores[domain] = domain_scores[domain] / domain_weights[domain]
            else:
                # No events/findings, default to baseline (20)
                domain_scores[domain] = 20.0
            
            # Clamp to 0-100
            domain_scores[domain] = max(0, min(100, domain_scores[domain]))
        
        return domain_scores
    
    def generate_radar_chart(
        self,
        state: AssessmentState,
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Generate a Plotly radar chart from assessment state.
        
        Args:
            state: Assessment state
            title: Chart title (optional)
            
        Returns:
            Plotly Figure object
        """
        domain_scores = self.calculate_domain_scores(state)
        
        # Prepare data for radar chart
        categories = self.DOMAINS
        values = [domain_scores[domain] for domain in categories]
        
        # Create radar chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Security Posture',
            line_color='rgb(0, 123, 255)',
            fillcolor='rgba(0, 123, 255, 0.2)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(size=10)
                ),
                angularaxis=dict(
                    tickfont=dict(size=12)
                )
            ),
            showlegend=True,
            title=title or f"SecAI Radar - Security Posture (Phase: {state.get('phase')})",
            height=600,
            width=800
        )
        
        return fig
    
    def generate_chart_json(
        self,
        state: AssessmentState
    ) -> Dict[str, Any]:
        """
        Generate radar chart data as JSON for frontend consumption.
        
        Args:
            state: Assessment state
            
        Returns:
            Dictionary with chart data
        """
        domain_scores = self.calculate_domain_scores(state)
        
        return {
            "domains": self.DOMAINS,
            "scores": [domain_scores[domain] for domain in self.DOMAINS],
            "overall_score": sum(domain_scores.values()) / len(domain_scores),
            "phase": str(state.get("phase")),
            "timestamp": state.get("updated_at").isoformat() if hasattr(state.get("updated_at"), "isoformat") else str(state.get("updated_at"))
        }

