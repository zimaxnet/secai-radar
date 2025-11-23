"""
RAG Factory

Creates and configures RAG retrievers based on configuration.
"""

import os
import yaml
from pathlib import Path
from typing import Optional

from .google_file_search import GoogleFileSearchRetriever
from .agentic_retrieval import AgenticRetriever
from .base_retriever import BaseRetriever


def load_rag_config(config_path: Optional[Path] = None) -> dict:
    """
    Load RAG configuration from YAML file.
    
    Args:
        config_path: Path to rag.yaml. If None, uses default location.
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        # Default to config/rag.yaml relative to project root
        project_root = Path(__file__).resolve().parents[2]
        config_path = project_root / "config" / "rag.yaml"
    
    if not config_path.exists():
        # Return default config if file doesn't exist
        return {
            "provider": "google_file_search",
            "agentic_retrieval": {"enabled": True}
        }
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def create_rag_retriever(
    config: Optional[dict] = None,
    model_layer=None
) -> Optional[BaseRetriever]:
    """
    Create a RAG retriever based on configuration.
    
    Args:
        config: RAG configuration dict. If None, loads from config/rag.yaml
        model_layer: Model Layer instance (for agentic retrieval)
        
    Returns:
        BaseRetriever instance, or None if not configured
    """
    if config is None:
        config = load_rag_config()
    
    provider = config.get("provider", "google_file_search")
    
    if provider == "google_file_search":
        return _create_google_file_search_retriever(config)
    elif provider == "azure_ai_search":
        # Azure AI Search not yet implemented
        print("Warning: Azure AI Search not yet implemented, using Google File Search")
        return _create_google_file_search_retriever(config)
    else:
        print(f"Warning: Unknown RAG provider '{provider}', using Google File Search")
        return _create_google_file_search_retriever(config)


def _create_google_file_search_retriever(config: dict) -> Optional[GoogleFileSearchRetriever]:
    """Create Google File Search retriever"""
    google_config = config.get("google_file_search", {})
    
    api_key_env = google_config.get("api_key_env", "GOOGLE_API_KEY")
    file_store_id_env = google_config.get("file_store_id_env", "GOOGLE_FILE_STORE_ID")
    
    api_key = os.getenv(api_key_env)
    file_store_id = os.getenv(file_store_id_env)
    
    if not api_key:
        print(f"Warning: {api_key_env} not set, RAG will not be available")
        return None
    
    try:
        return GoogleFileSearchRetriever(
            api_key=api_key,
            file_store_id=file_store_id
        )
    except Exception as e:
        print(f"Error creating Google File Search retriever: {e}")
        return None


def create_agentic_retriever(
    base_retriever: Optional[BaseRetriever],
    config: Optional[dict] = None,
    model_layer=None
) -> Optional[AgenticRetriever]:
    """
    Wrap base retriever with agentic retrieval capabilities.
    
    Args:
        base_retriever: Base retriever instance
        config: RAG configuration dict
        model_layer: Model Layer instance
        
    Returns:
        AgenticRetriever instance, or base_retriever if agentic not enabled
    """
    if base_retriever is None:
        return None
    
    if config is None:
        config = load_rag_config()
    
    agentic_config = config.get("agentic_retrieval", {})
    enabled = agentic_config.get("enabled", True)
    
    if enabled:
        return AgenticRetriever(
            retriever=base_retriever,
            model_layer=model_layer
        )
    else:
        # Return base retriever without agentic wrapper
        return base_retriever


def get_rag_retriever(
    model_layer=None,
    config_path: Optional[Path] = None
) -> Optional[BaseRetriever]:
    """
    Get configured RAG retriever (convenience function).
    
    This function:
    1. Loads RAG configuration
    2. Creates base retriever (Google File Search, etc.)
    3. Wraps with AgenticRetriever if enabled
    
    Args:
        model_layer: Model Layer instance (for agentic retrieval)
        config_path: Path to rag.yaml config file
        
    Returns:
        Configured retriever (AgenticRetriever or BaseRetriever), or None
    """
    config = load_rag_config(config_path)
    
    # Create base retriever
    base_retriever = create_rag_retriever(config, model_layer)
    
    if base_retriever is None:
        return None
    
    # Wrap with agentic retrieval if enabled
    return create_agentic_retriever(base_retriever, config, model_layer)

