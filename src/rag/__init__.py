"""
RAG Layer Module

Retrieval-Augmented Generation for agent knowledge base queries.
Supports both Google File Search and Azure AI Search.
"""

from .base_retriever import BaseRetriever
from .google_file_search import GoogleFileSearchRetriever
from .agentic_retrieval import AgenticRetriever
from .factory import (
    load_rag_config,
    create_rag_retriever,
    create_agentic_retriever,
    get_rag_retriever
)

__all__ = [
    "BaseRetriever",
    "GoogleFileSearchRetriever",
    "AgenticRetriever",
    "load_rag_config",
    "create_rag_retriever",
    "create_agentic_retriever",
    "get_rag_retriever"
]

