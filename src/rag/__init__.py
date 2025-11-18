"""
RAG Layer Module

Retrieval-Augmented Generation for agent knowledge base queries.
Supports both Google File Search and Azure AI Search.
"""

from .base_retriever import BaseRetriever
from .google_file_search import GoogleFileSearchRetriever
from .agentic_retrieval import AgenticRetriever

__all__ = [
    "BaseRetriever",
    "GoogleFileSearchRetriever",
    "AgenticRetriever"
]

