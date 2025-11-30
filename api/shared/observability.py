"""
Agent Observability Service

Provides comprehensive observability for SecAI Radar agents using OpenTelemetry.
Tracks agent actions, tool calls, performance metrics, and evaluation scores.
"""

import os
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextlib import contextmanager

try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from azure.monitor.opentelemetry import configure_azure_monitor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    trace = None
    metrics = None

logger = logging.getLogger(__name__)


class AgentObservability:
    """
    Service for tracking agent observability metrics and traces.
    
    Provides:
    - End-to-end tracing of agent actions
    - Performance metrics (latency, token usage, success rates)
    - Evaluation score tracking
    - Tool call monitoring
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize observability service.
        
        Args:
            connection_string: Application Insights connection string
        """
        self.connection_string = connection_string or os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        
        # Initialize OpenTelemetry if available
        if OPENTELEMETRY_AVAILABLE:
            try:
                # Configure Azure Monitor exporter
                if self.connection_string:
                    configure_azure_monitor(connection_string=self.connection_string)
                    logger.info("Azure Monitor OpenTelemetry configured")
                else:
                    # Use default SDK setup (console exporter for development)
                    from opentelemetry.sdk.trace.export import ConsoleSpanExporter
                    provider = TracerProvider()
                    processor = BatchSpanProcessor(ConsoleSpanExporter())
                    provider.add_span_processor(processor)
                    trace.set_tracer_provider(provider)
                    logger.info("OpenTelemetry configured with console exporter")
                
                # Get tracer and meter
                self.tracer = trace.get_tracer(__name__)
                self.meter = metrics.get_meter(__name__)
                
                # Create metrics
                self._create_metrics()
                
            except Exception as e:
                logger.warning(f"Could not initialize OpenTelemetry: {e}")
                self.tracer = None
                self.meter = None
        else:
            logger.warning("OpenTelemetry not available")
            self.tracer = None
            self.meter = None
    
    def _create_metrics(self):
        """Create custom metrics for agent observability"""
        if not self.meter:
            return
        
        # Response time histogram
        self.response_time_histogram = self.meter.create_histogram(
            name="agent_response_time_ms",
            description="Agent response time in milliseconds",
            unit="ms"
        )
        
        # Token usage counter
        self.token_usage_counter = self.meter.create_counter(
            name="agent_token_usage",
            description="Total tokens consumed by agents",
            unit="tokens"
        )
        
        # Tool call counter
        self.tool_call_counter = self.meter.create_counter(
            name="agent_tool_calls",
            description="Number of tool calls made by agents",
            unit="calls"
        )
        
        # Success/failure counter
        self.action_counter = self.meter.create_counter(
            name="agent_actions",
            description="Agent actions (success/failure)",
            unit="actions"
        )
        
        # Evaluation score gauge
        self.evaluation_gauge = self.meter.create_up_down_counter(
            name="agent_evaluation_score",
            description="Agent evaluation scores (0-1)",
            unit="score"
        )
    
    @contextmanager
    def trace_agent_action(
        self,
        agent_id: str,
        action: str,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager for tracing an agent action.
        
        Usage:
            with observability.trace_agent_action(agent_id, "process_task"):
                # Agent action code
                pass
        
        Args:
            agent_id: Agent identifier
            action: Action name (e.g., "process_task", "tool_call")
            attributes: Optional additional attributes
        """
        if not self.tracer:
            yield
            return
        
        span_name = f"agent.{agent_id}.{action}"
        span_attributes = {
            "agent.id": agent_id,
            "agent.action": action
        }
        if attributes:
            span_attributes.update(attributes)
        
        with self.tracer.start_as_current_span(span_name, attributes=span_attributes) as span:
            start_time = time.time()
            try:
                yield span
                duration_ms = (time.time() - start_time) * 1000
                
                # Record duration
                span.set_attribute("duration_ms", duration_ms)
                span.set_status(trace.Status(trace.StatusCode.OK))
                
                # Record metric
                if self.response_time_histogram:
                    self.response_time_histogram.record(duration_ms, {
                        "agent.id": agent_id,
                        "agent.action": action
                    })
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                span.set_attribute("duration_ms", duration_ms)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
    
    def record_evaluation(
        self,
        agent_id: str,
        evaluation_type: str,
        score: float,
        attributes: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record an evaluation score for an agent.
        
        Args:
            agent_id: Agent identifier
            evaluation_type: Type of evaluation (groundedness, task_adherence, tool_accuracy)
            score: Evaluation score (0-1)
            attributes: Optional additional attributes
        """
        if not self.meter:
            return
        
        # Record as metric
        metric_attributes = {
            "agent.id": agent_id,
            "evaluation.type": evaluation_type
        }
        if attributes:
            metric_attributes.update(attributes)
        
        # Use gauge to record current score
        if self.evaluation_gauge:
            self.evaluation_gauge.add(score, metric_attributes)
        
        # Also create a span for the evaluation
        if self.tracer:
            with self.tracer.start_as_current_span(
                f"agent.{agent_id}.evaluation.{evaluation_type}",
                attributes={
                    "agent.id": agent_id,
                    "evaluation.type": evaluation_type,
                    "evaluation.score": score,
                    **(attributes or {})
                }
            ) as span:
                span.set_status(trace.Status(trace.StatusCode.OK))
        
        logger.debug(f"Recorded evaluation: {agent_id} - {evaluation_type} = {score}")
    
    def track_tool_call(
        self,
        agent_id: str,
        tool_name: str,
        success: bool,
        duration_ms: float,
        attributes: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Track a tool call made by an agent.
        
        Args:
            agent_id: Agent identifier
            tool_name: Name of the tool called
            success: Whether the tool call succeeded
            duration_ms: Duration in milliseconds
            attributes: Optional additional attributes
        """
        if not self.meter:
            return
        
        metric_attributes = {
            "agent.id": agent_id,
            "tool.name": tool_name,
            "tool.success": str(success)
        }
        if attributes:
            metric_attributes.update(attributes)
        
        # Increment tool call counter
        if self.tool_call_counter:
            self.tool_call_counter.add(1, metric_attributes)
        
        # Record response time
        if self.response_time_histogram:
            self.response_time_histogram.record(duration_ms, metric_attributes)
        
        # Record success/failure
        if self.action_counter:
            status = "success" if success else "failure"
            self.action_counter.add(1, {
                **metric_attributes,
                "action.status": status
            })
        
        # Create span for tool call
        if self.tracer:
            with self.tracer.start_as_current_span(
                f"agent.{agent_id}.tool.{tool_name}",
                attributes={
                    "agent.id": agent_id,
                    "tool.name": tool_name,
                    "tool.success": success,
                    "tool.duration_ms": duration_ms,
                    **(attributes or {})
                }
            ) as span:
                if not success:
                    span.set_status(trace.Status(trace.StatusCode.ERROR))
        
        logger.debug(f"Tracked tool call: {agent_id} -> {tool_name} ({'success' if success else 'failure'})")
    
    def record_token_usage(
        self,
        agent_id: str,
        tokens: int,
        token_type: str = "total",
        attributes: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record token usage for an agent.
        
        Args:
            agent_id: Agent identifier
            tokens: Number of tokens used
            token_type: Type of tokens (prompt, completion, total)
            attributes: Optional additional attributes
        """
        if not self.meter:
            return
        
        metric_attributes = {
            "agent.id": agent_id,
            "token.type": token_type
        }
        if attributes:
            metric_attributes.update(attributes)
        
        if self.token_usage_counter:
            self.token_usage_counter.add(tokens, metric_attributes)
        
        logger.debug(f"Recorded token usage: {agent_id} - {token_type} = {tokens}")
    
    def record_agent_action(
        self,
        agent_id: str,
        action: str,
        success: bool,
        attributes: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a general agent action.
        
        Args:
            agent_id: Agent identifier
            action: Action name
            success: Whether the action succeeded
            attributes: Optional additional attributes
        """
        if not self.meter:
            return
        
        metric_attributes = {
            "agent.id": agent_id,
            "action.name": action,
            "action.status": "success" if success else "failure"
        }
        if attributes:
            metric_attributes.update(attributes)
        
        if self.action_counter:
            self.action_counter.add(1, metric_attributes)
        
        logger.debug(f"Recorded action: {agent_id} - {action} ({'success' if success else 'failure'})")


# Singleton instance
_observability_service: Optional[AgentObservability] = None


def get_observability_service() -> AgentObservability:
    """Get or create the observability service instance"""
    global _observability_service
    if _observability_service is None:
        _observability_service = AgentObservability()
    return _observability_service

