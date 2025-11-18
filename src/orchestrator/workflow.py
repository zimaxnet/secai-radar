"""
Three-Phase Workflow Implementation

Orchestrates the complete assessment workflow through three phases:
1. Assessment and Discovery
2. Design and Conflict Resolution
3. Migration Planning
"""

from typing import Dict, Any, Optional
from .state import AssessmentState, AssessmentPhase, StateManager
from .supervisor import Supervisor
from .handoff import HandoffManager
from .phases import AssessmentPhase as AssessmentPhaseHandler, DesignPhase, MigrationPhase


class WorkflowOrchestrator:
    """
    Orchestrates the three-phase assessment workflow.
    """
    
    def __init__(
        self,
        state_manager: StateManager,
        supervisor: Supervisor,
        handoff_manager: HandoffManager
    ):
        """
        Initialize WorkflowOrchestrator.
        
        Args:
            state_manager: StateManager instance
            supervisor: Supervisor instance
            handoff_manager: HandoffManager instance
        """
        self.state_manager = state_manager
        self.supervisor = supervisor
        self.handoff_manager = handoff_manager
    
    async def execute_phase(
        self,
        state: AssessmentState,
        phase: AssessmentPhase
    ) -> AssessmentState:
        """
        Execute a specific workflow phase.
        
        Args:
            state: Current assessment state
            phase: Phase to execute
            
        Returns:
            Updated state after phase execution
        """
        if phase == AssessmentPhase.ASSESSMENT:
            return await self._execute_assessment_phase(state)
        elif phase == AssessmentPhase.DESIGN:
            return await self._execute_design_phase(state)
        elif phase == AssessmentPhase.MIGRATION:
            return await self._execute_migration_phase(state)
        else:
            return state
    
    async def _execute_assessment_phase(self, state: AssessmentState) -> AssessmentState:
        """Execute Phase 1: Assessment and Discovery"""
        phase_handler = AssessmentPhaseHandler
        
        while not phase_handler.is_complete(state):
            next_task = phase_handler.get_next_task(state)
            
            if not next_task.get("agent"):
                break
            
            # Create handoff for the task
            handoff = await self.handoff_manager.create_handoff(
                state,
                from_agent="supervisor",
                to_agent=next_task["agent"],
                task_description=next_task["task"]
            )
            
            # Apply handoff
            state = self.handoff_manager.apply_handoff(state, handoff)
            
            # Route through supervisor (which will delegate to agent)
            state = self.supervisor.route(state)
        
        return state
    
    async def _execute_design_phase(self, state: AssessmentState) -> AssessmentState:
        """Execute Phase 2: Design and Conflict Resolution"""
        phase_handler = DesignPhase
        
        while not phase_handler.is_complete(state):
            next_task = phase_handler.get_next_task(state)
            
            if not next_task.get("agent"):
                break
            
            # Create handoff
            handoff = await self.handoff_manager.create_handoff(
                state,
                from_agent="supervisor",
                to_agent=next_task["agent"],
                task_description=next_task["task"]
            )
            
            # Apply handoff
            state = self.handoff_manager.apply_handoff(state, handoff)
            
            # Route through supervisor
            state = self.supervisor.route(state)
        
        return state
    
    async def _execute_migration_phase(self, state: AssessmentState) -> AssessmentState:
        """Execute Phase 3: Migration Planning"""
        phase_handler = MigrationPhase
        
        while not phase_handler.is_complete(state):
            next_task = phase_handler.get_next_task(state)
            
            if not next_task.get("agent"):
                break
            
            # Create handoff
            handoff = await self.handoff_manager.create_handoff(
                state,
                from_agent="supervisor",
                to_agent=next_task["agent"],
                task_description=next_task["task"]
            )
            
            # Apply handoff
            state = self.handoff_manager.apply_handoff(state, handoff)
            
            # Route through supervisor
            state = self.supervisor.route(state)
        
        return state

