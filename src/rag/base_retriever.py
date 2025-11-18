"""
Base RAG Retriever Interface

Abstract base class for RAG retrieval implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseRetriever(ABC):
    """
    Abstract base class for RAG retrievers.
    Provides interface for knowledge base queries.
    """
    
    @abstractmethod
    async def retrieve(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> Optional[str]:
        """
        Retrieve relevant context from knowledge base.
        
        Args:
            query: Search query
            context: Additional context for the query
            top_k: Number of results to return
            
        Returns:
            Retrieved context as string, or None if no results
        """
        pass
    
    @abstractmethod
    async def upload_document(
        self,
        document_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Upload a document to the knowledge base.
        
        Args:
            document_path: Path to document file
            metadata: Document metadata
            
        Returns:
            True if successful
        """
        pass

