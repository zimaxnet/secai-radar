"""
Model Layer Adapter

Bridges the existing Azure OpenAI service with the multi-agent system interface.
"""

import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path

# Add api directory to path to import shared modules
api_path = Path(__file__).resolve().parents[2] / "api"
if str(api_path) not in sys.path:
    sys.path.insert(0, str(api_path))

try:
    from shared.ai_service import get_ai_service, AzureOpenAIService
    AI_SERVICE_AVAILABLE = True
except (ImportError, ValueError):
    AI_SERVICE_AVAILABLE = False
    AzureOpenAIService = None


class ModelLayer:
    """
    Model Layer adapter that provides a unified interface for agent LLM access.
    
    Wraps the existing Azure OpenAI service to match the interface expected by agents.
    """
    
    def __init__(self, ai_service: Optional[AzureOpenAIService] = None):
        """
        Initialize Model Layer.
        
        Args:
            ai_service: AzureOpenAIService instance (or None to auto-initialize)
        """
        if ai_service:
            self.ai_service = ai_service
        elif AI_SERVICE_AVAILABLE:
            try:
                self.ai_service = get_ai_service()
            except (ValueError, Exception) as e:
                print(f"Warning: Could not initialize AI service: {e}")
                self.ai_service = None
        else:
            self.ai_service = None
    
    async def reasoning(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform reasoning task using the model.
        
        Args:
            prompt: Reasoning prompt/question
            context: Additional context dictionary
            
        Returns:
            Dict with 'content' key containing the response
        """
        if not self.ai_service:
            return {
                "content": "Model layer not available. AI service not configured.",
                "error": True
            }
        
        try:
            # Build messages from prompt and context
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert security consultant. Provide clear, reasoned analysis based on the given context."
                }
            ]
            
            # Add context if provided
            if context:
                context_str = self._format_context(context)
                user_content = f"Context:\n{context_str}\n\nTask:\n{prompt}"
            else:
                user_content = prompt
            
            messages.append({"role": "user", "content": user_content})
            
            # Call AI service
            response = self.ai_service.chat_completion(
                messages=messages,
                stream=False,
                temperature=0.7,
                max_tokens=4096
            )
            
            content = response.choices[0].message.content
            
            return {
                "content": content,
                "error": False
            }
        except Exception as e:
            print(f"Error in reasoning: {e}")
            return {
                "content": f"Error during reasoning: {str(e)}",
                "error": True
            }
    
    async def classify(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform classification task using the model.
        
        Args:
            context: Context dictionary to classify
            
        Returns:
            Dict with 'content' key containing classification result
        """
        if not self.ai_service:
            return {
                "content": "Model layer not available. AI service not configured.",
                "error": True
            }
        
        try:
            # Format context for classification
            context_str = self._format_context(context)
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a classification expert. Analyze the provided context and classify it appropriately. Respond with JSON format when possible."
                },
                {
                    "role": "user",
                    "content": f"Classify the following context:\n\n{context_str}\n\nProvide a classification with reasoning."
                }
            ]
            
            response = self.ai_service.chat_completion(
                messages=messages,
                stream=False,
                temperature=0.3,
                max_tokens=2048
            )
            
            content = response.choices[0].message.content
            
            return {
                "content": content,
                "error": False
            }
        except Exception as e:
            print(f"Error in classification: {e}")
            return {
                "content": f"Error during classification: {str(e)}",
                "error": True
            }
    
    async def generate(
        self,
        section_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate content for a specific section type.
        
        Args:
            section_type: Type of section to generate (e.g., "findings", "recommendations")
            data: Data dictionary to use for generation
            
        Returns:
            Dict with 'content' key containing generated content
        """
        if not self.ai_service:
            return {
                "content": "Model layer not available. AI service not configured.",
                "error": True
            }
        
        try:
            # Format data for generation
            data_str = self._format_context(data)
            
            messages = [
                {
                    "role": "system",
                    "content": f"You are a security assessment expert. Generate professional, accurate content for {section_type} sections."
                },
                {
                    "role": "user",
                    "content": f"Generate a {section_type} section based on the following data:\n\n{data_str}\n\nProvide comprehensive, actionable content."
                }
            ]
            
            response = self.ai_service.chat_completion(
                messages=messages,
                stream=False,
                temperature=0.8,
                max_tokens=4096
            )
            
            content = response.choices[0].message.content
            
            return {
                "content": content,
                "error": False
            }
        except Exception as e:
            print(f"Error in generation: {e}")
            return {
                "content": f"Error during generation: {str(e)}",
                "error": True
            }
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """
        Format context dictionary into a readable string.
        
        Args:
            context: Context dictionary
            
        Returns:
            Formatted string
        """
        if not context:
            return ""
        
        parts = []
        for key, value in context.items():
            if isinstance(value, (dict, list)):
                import json
                parts.append(f"{key}:\n{json.dumps(value, indent=2)}")
            else:
                parts.append(f"{key}: {value}")
        
        return "\n".join(parts)


# Singleton instance
_model_layer_instance: Optional[ModelLayer] = None


def get_model_layer() -> ModelLayer:
    """
    Get or create the Model Layer instance.
    
    Returns:
        ModelLayer instance
    """
    global _model_layer_instance
    if _model_layer_instance is None:
        _model_layer_instance = ModelLayer()
    return _model_layer_instance

