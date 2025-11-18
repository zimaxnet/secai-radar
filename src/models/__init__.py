"""
Model Layer for Multi-Agent System

Provides a unified interface for LLM access across all agents.
"""

from .model_layer import ModelLayer, get_model_layer

__all__ = ["ModelLayer", "get_model_layer"]

