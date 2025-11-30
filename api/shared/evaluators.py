"""
AI-Powered Agent Evaluators

Provides continuous evaluation of agent performance using AI-powered evaluators.
Evaluates groundedness, task adherence, tool accuracy, and relevance.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from shared.ai_service import get_ai_service
from shared.observability import get_observability_service

logger = logging.getLogger(__name__)


class AgentEvaluator:
    """
    Service for evaluating agent performance using AI-powered evaluators.
    
    Provides:
    - Groundedness evaluation (responses grounded in context)
    - Task adherence evaluation (agent followed instructions)
    - Tool accuracy evaluation (tool calls were correct)
    - Relevance evaluation (response relevant to query)
    """
    
    def __init__(self):
        """Initialize the evaluator service"""
        try:
            self.ai_service = get_ai_service()
        except Exception as e:
            logger.warning(f"AI service not available for evaluators: {e}")
            self.ai_service = None
        
        self.observability = get_observability_service()
    
    def evaluate_groundedness(
        self,
        response: str,
        context: str,
        agent_id: Optional[str] = None
    ) -> float:
        """
        Evaluate if a response is grounded in the provided context.
        
        Args:
            response: Agent response text
            context: Context that should ground the response
            agent_id: Optional agent identifier for tracking
            
        Returns:
            Groundedness score (0-1), where 1.0 means fully grounded
        """
        if not self.ai_service:
            logger.warning("AI service not available, returning default groundedness score")
            return 0.5
        
        system_prompt = """You are an evaluator assessing whether an AI agent's response is grounded in the provided context.

A response is "grounded" if:
1. The information in the response can be traced back to the context
2. The response doesn't make unsupported claims
3. The response doesn't hallucinate facts not in the context

Rate the groundedness on a scale of 0.0 to 1.0:
- 1.0: Fully grounded, all claims supported by context
- 0.7-0.9: Mostly grounded, minor unsupported claims
- 0.4-0.6: Partially grounded, some unsupported claims
- 0.1-0.3: Mostly ungrounded, many unsupported claims
- 0.0: Completely ungrounded, no connection to context

Respond with ONLY a number between 0.0 and 1.0."""
        
        user_prompt = f"""Context:
{context}

Agent Response:
{response}

Rate the groundedness of the response (0.0-1.0):"""
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response_obj = self.ai_service.chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=50
            )
            
            score_text = response_obj.choices[0].message.content.strip()
            # Extract numeric score
            try:
                score = float(score_text.split()[0])
                score = max(0.0, min(1.0, score))  # Clamp to 0-1
            except (ValueError, IndexError):
                logger.warning(f"Could not parse groundedness score: {score_text}")
                score = 0.5
            
            # Record evaluation
            if agent_id:
                self.observability.record_evaluation(
                    agent_id=agent_id,
                    evaluation_type="groundedness",
                    score=score
                )
            
            logger.debug(f"Groundedness evaluation: {score:.2f}")
            return score
        
        except Exception as e:
            logger.error(f"Error evaluating groundedness: {e}")
            return 0.5
    
    def evaluate_task_adherence(
        self,
        response: str,
        task_instruction: str,
        agent_id: Optional[str] = None
    ) -> float:
        """
        Evaluate if an agent followed the assigned task instructions.
        
        Args:
            response: Agent response text
            task_instruction: Original task instruction
            agent_id: Optional agent identifier for tracking
            
        Returns:
            Task adherence score (0-1), where 1.0 means fully adhered
        """
        if not self.ai_service:
            logger.warning("AI service not available, returning default task adherence score")
            return 0.5
        
        system_prompt = """You are an evaluator assessing whether an AI agent followed the assigned task instructions.

A response "adheres" to the task if:
1. It addresses all parts of the task instruction
2. It follows the specified format or structure (if any)
3. It doesn't deviate from the task scope
4. It provides the requested information or action

Rate the task adherence on a scale of 0.0 to 1.0:
- 1.0: Fully adheres, all requirements met
- 0.7-0.9: Mostly adheres, minor deviations
- 0.4-0.6: Partially adheres, some requirements missed
- 0.1-0.3: Mostly doesn't adhere, major deviations
- 0.0: Completely off-task

Respond with ONLY a number between 0.0 and 1.0."""
        
        user_prompt = f"""Task Instruction:
{task_instruction}

Agent Response:
{response}

Rate the task adherence (0.0-1.0):"""
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response_obj = self.ai_service.chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=50
            )
            
            score_text = response_obj.choices[0].message.content.strip()
            try:
                score = float(score_text.split()[0])
                score = max(0.0, min(1.0, score))
            except (ValueError, IndexError):
                logger.warning(f"Could not parse task adherence score: {score_text}")
                score = 0.5
            
            # Record evaluation
            if agent_id:
                self.observability.record_evaluation(
                    agent_id=agent_id,
                    evaluation_type="task_adherence",
                    score=score
                )
            
            logger.debug(f"Task adherence evaluation: {score:.2f}")
            return score
        
        except Exception as e:
            logger.error(f"Error evaluating task adherence: {e}")
            return 0.5
    
    def evaluate_tool_accuracy(
        self,
        tool_calls: List[Dict[str, Any]],
        expected_behavior: Optional[str] = None,
        actual_results: Optional[List[Any]] = None,
        agent_id: Optional[str] = None
    ) -> float:
        """
        Evaluate if tool calls were accurate and correct.
        
        Args:
            tool_calls: List of tool calls made by agent
            expected_behavior: Optional description of expected behavior
            actual_results: Optional actual results from tool calls
            agent_id: Optional agent identifier for tracking
            
        Returns:
            Tool accuracy score (0-1), where 1.0 means all tools used correctly
        """
        if not tool_calls:
            return 1.0  # No tool calls = perfect accuracy
        
        if not self.ai_service:
            logger.warning("AI service not available, returning default tool accuracy score")
            return 0.5
        
        system_prompt = """You are an evaluator assessing whether an AI agent made accurate and correct tool calls.

Tool calls are "accurate" if:
1. The tool selected is appropriate for the task
2. The parameters provided are correct and valid
3. The tool was used in the right sequence
4. The results match expectations (if provided)

Rate the tool accuracy on a scale of 0.0 to 1.0:
- 1.0: All tool calls accurate and correct
- 0.7-0.9: Mostly accurate, minor issues
- 0.4-0.6: Partially accurate, some incorrect calls
- 0.1-0.3: Mostly inaccurate, many incorrect calls
- 0.0: Completely inaccurate

Respond with ONLY a number between 0.0 and 1.0."""
        
        tool_calls_text = "\n".join([
            f"Tool: {tc.get('tool_name', 'unknown')}, "
            f"Params: {tc.get('parameters', {})}, "
            f"Success: {tc.get('success', False)}"
            for tc in tool_calls
        ])
        
        user_prompt = f"""Tool Calls Made:
{tool_calls_text}
"""
        
        if expected_behavior:
            user_prompt += f"\nExpected Behavior: {expected_behavior}"
        
        if actual_results:
            user_prompt += f"\nActual Results: {actual_results}"
        
        user_prompt += "\n\nRate the tool accuracy (0.0-1.0):"
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response_obj = self.ai_service.chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=50
            )
            
            score_text = response_obj.choices[0].message.content.strip()
            try:
                score = float(score_text.split()[0])
                score = max(0.0, min(1.0, score))
            except (ValueError, IndexError):
                logger.warning(f"Could not parse tool accuracy score: {score_text}")
                score = 0.5
            
            # Record evaluation
            if agent_id:
                self.observability.record_evaluation(
                    agent_id=agent_id,
                    evaluation_type="tool_accuracy",
                    score=score
                )
            
            logger.debug(f"Tool accuracy evaluation: {score:.2f}")
            return score
        
        except Exception as e:
            logger.error(f"Error evaluating tool accuracy: {e}")
            return 0.5
    
    def evaluate_relevance(
        self,
        response: str,
        query: str,
        agent_id: Optional[str] = None
    ) -> float:
        """
        Evaluate if a response is relevant to the query.
        
        Args:
            response: Agent response text
            query: Original query/question
            agent_id: Optional agent identifier for tracking
            
        Returns:
            Relevance score (0-1), where 1.0 means highly relevant
        """
        if not self.ai_service:
            logger.warning("AI service not available, returning default relevance score")
            return 0.5
        
        system_prompt = """You are an evaluator assessing whether an AI agent's response is relevant to the query.

A response is "relevant" if:
1. It directly addresses the query
2. It provides information related to the query
3. It doesn't go off-topic
4. It's useful for answering the query

Rate the relevance on a scale of 0.0 to 1.0:
- 1.0: Highly relevant, directly answers query
- 0.7-0.9: Mostly relevant, addresses query well
- 0.4-0.6: Partially relevant, some off-topic content
- 0.1-0.3: Mostly irrelevant, doesn't address query
- 0.0: Completely irrelevant

Respond with ONLY a number between 0.0 and 1.0."""
        
        user_prompt = f"""Query:
{query}

Agent Response:
{response}

Rate the relevance (0.0-1.0):"""
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response_obj = self.ai_service.chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=50
            )
            
            score_text = response_obj.choices[0].message.content.strip()
            try:
                score = float(score_text.split()[0])
                score = max(0.0, min(1.0, score))
            except (ValueError, IndexError):
                logger.warning(f"Could not parse relevance score: {score_text}")
                score = 0.5
            
            # Record evaluation
            if agent_id:
                self.observability.record_evaluation(
                    agent_id=agent_id,
                    evaluation_type="relevance",
                    score=score
                )
            
            logger.debug(f"Relevance evaluation: {score:.2f}")
            return score
        
        except Exception as e:
            logger.error(f"Error evaluating relevance: {e}")
            return 0.5
    
    def run_comprehensive_evaluation(
        self,
        agent_id: str,
        response: str,
        context: Optional[str] = None,
        task_instruction: Optional[str] = None,
        query: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, float]:
        """
        Run a comprehensive evaluation with all available evaluators.
        
        Args:
            agent_id: Agent identifier
            response: Agent response text
            context: Optional context for groundedness evaluation
            task_instruction: Optional task instruction for adherence evaluation
            query: Optional query for relevance evaluation
            tool_calls: Optional tool calls for accuracy evaluation
            
        Returns:
            Dictionary of evaluation scores
        """
        scores = {}
        
        if context:
            scores["groundedness"] = self.evaluate_groundedness(
                response, context, agent_id
            )
        
        if task_instruction:
            scores["task_adherence"] = self.evaluate_task_adherence(
                response, task_instruction, agent_id
            )
        
        if query:
            scores["relevance"] = self.evaluate_relevance(
                response, query, agent_id
            )
        
        if tool_calls:
            scores["tool_accuracy"] = self.evaluate_tool_accuracy(
                tool_calls, agent_id=agent_id
            )
        
        return scores


# Singleton instance
_evaluator_service: Optional[AgentEvaluator] = None


def get_evaluator_service() -> AgentEvaluator:
    """Get or create the evaluator service instance"""
    global _evaluator_service
    if _evaluator_service is None:
        _evaluator_service = AgentEvaluator()
    return _evaluator_service

