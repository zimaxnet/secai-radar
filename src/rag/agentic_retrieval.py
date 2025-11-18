"""
Agentic RAG Retrieval

Implements agentic retrieval pattern where agents decide when to search
and generate their own queries based on context.
"""

from typing import Dict, Any, Optional, Tuple
from .base_retriever import BaseRetriever


class AgenticRetriever:
    """
    Agentic RAG retriever that allows agents to decide when and how to search.
    
    This implements the "Agentic RAG" pattern where:
    - Agents decide if retrieval is necessary
    - Agents generate their own search queries
    - Agents evaluate retrieved documents for relevance
    """
    
    def __init__(self, retriever: BaseRetriever, model_layer=None):
        """
        Initialize Agentic Retriever.
        
        Args:
            retriever: Base retriever implementation (Google File Search, Azure AI Search, etc.)
            model_layer: Model Layer for query generation and relevance evaluation
        """
        self.retriever = retriever
        self.model_layer = model_layer
    
    async def should_retrieve(
        self,
        agent_context: str,
        task_description: str
    ) -> bool:
        """
        Determine if retrieval is necessary for the given context.
        
        Args:
            agent_context: Current agent context
            task_description: Task being performed
            
        Returns:
            True if retrieval is recommended
        """
        if not self.model_layer:
            # Without model layer, always retrieve if task suggests it
            retrieval_keywords = ["caf", "mca", "azure", "landing zone", "security", "framework"]
            return any(keyword in task_description.lower() for keyword in retrieval_keywords)
        
        prompt = f"""
        Determine if the agent needs to search the knowledge base for this task.
        
        Task: {task_description}
        Context: {agent_context[:500]}
        
        Return 'yes' if knowledge base search would be helpful, 'no' otherwise.
        """
        
        try:
            result = await self.model_layer.reasoning(prompt)
            decision = result.get("content", "").lower()
            return "yes" in decision or "true" in decision
        except Exception:
            # Default to retrieving if model call fails
            return True
    
    async def generate_query(
        self,
        task_description: str,
        agent_context: Optional[str] = None
    ) -> str:
        """
        Generate a search query from task description and context.
        
        Args:
            task_description: Task being performed
            agent_context: Additional agent context
            
        Returns:
            Generated search query
        """
        if not self.model_layer:
            # Simple keyword extraction
            return task_description
        
        prompt = f"""
        Generate a concise search query for the knowledge base based on this task.
        
        Task: {task_description}
        {f"Context: {agent_context[:500]}" if agent_context else ""}
        
        Generate a focused search query (1-2 sentences max) that would retrieve
        relevant information from Azure CAF, MCA guides, or security best practices.
        """
        
        try:
            result = await self.model_layer.reasoning(prompt)
            query = result.get("content", "").strip()
            # Remove quotes if present
            query = query.strip('"').strip("'")
            return query or task_description
        except Exception:
            return task_description
    
    async def evaluate_relevance(
        self,
        retrieved_content: str,
        task_description: str
    ) -> Tuple[bool, str]:
        """
        Evaluate if retrieved content is relevant to the task.
        
        Args:
            retrieved_content: Content retrieved from knowledge base
            task_description: Original task description
            
        Returns:
            Tuple of (is_relevant, explanation)
        """
        if not self.model_layer:
            # Simple heuristic: if content is not empty, consider it relevant
            return len(retrieved_content) > 0, "Content retrieved"
        
        prompt = f"""
        Evaluate if the retrieved knowledge base content is relevant to this task.
        
        Task: {task_description}
        Retrieved Content: {retrieved_content[:1000]}
        
        Return 'relevant' or 'not relevant' with a brief explanation.
        """
        
        try:
            result = await self.model_layer.reasoning(prompt)
            evaluation = result.get("content", "").lower()
            is_relevant = "relevant" in evaluation and "not relevant" not in evaluation
            return is_relevant, result.get("content", "")
        except Exception:
            return True, "Evaluation unavailable"
    
    async def retrieve(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Retrieve context using the underlying retriever.
        
        Args:
            query: Search query
            context: Additional context
            
        Returns:
            Retrieved context or None
        """
        return await self.retriever.retrieve(query, context)
    
    async def agentic_retrieve(
        self,
        task_description: str,
        agent_context: Optional[str] = None
    ) -> Optional[str]:
        """
        Perform agentic retrieval: decide if needed, generate query, retrieve, evaluate.
        
        Args:
            task_description: Task being performed
            agent_context: Additional agent context
            
        Returns:
            Retrieved and evaluated context, or None
        """
        # Step 1: Decide if retrieval is needed
        should_retrieve = await self.should_retrieve(
            agent_context or "",
            task_description
        )
        
        if not should_retrieve:
            return None
        
        # Step 2: Generate search query
        query = await self.generate_query(task_description, agent_context)
        
        # Step 3: Retrieve from knowledge base
        retrieved_content = await self.retrieve(query, {
            "task": task_description,
            "agent_context": agent_context
        })
        
        if not retrieved_content:
            return None
        
        # Step 4: Evaluate relevance
        is_relevant, explanation = await self.evaluate_relevance(
            retrieved_content,
            task_description
        )
        
        if not is_relevant:
            # Content not relevant, return None
            return None
        
        # Return relevant content
        return retrieved_content

