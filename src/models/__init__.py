"""
SecAI Radar - Model Layer

This module provides role-based access to AI models according to the blueprint architecture.
Models are accessed by ROLE (reasoning, classification, generation), not by brand/provider.

Usage:
    from models import get_model
    
    reasoning = get_model("reasoning_model")
    response = await reasoning.analyze(evidence, context)
"""

from .config import ModelConfig, load_model_config
from .providers import ModelProvider, AzureOpenAIProvider
from .model_layer import ModelLayer, get_model

__all__ = [
    "ModelConfig",
    "load_model_config",
    "ModelProvider",
    "AzureOpenAIProvider",
    "ModelLayer",
    "get_model",
]

