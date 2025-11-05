"""
Model Layer - Role-Based Model Access

This module provides the Model Layer abstraction according to the blueprint.
Models are accessed by ROLE, not by brand/provider.
"""

from typing import Dict, List, Optional, Any
from .config import ModelConfig, load_model_config, get_role_config
from .providers import ModelProvider, create_provider


class ModelLayer:
    """
    Model Layer abstraction for role-based model access.
    
    Provides unified interface for accessing models by role:
    - reasoning_model: Multi-step security analysis
    - classification_model: Evidence classification
    - generation_model: Report generation
    """
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """
        Initialize Model Layer.
        
        Args:
            config: ModelConfig instance. If None, loads from default location.
        """
        if config is None:
            config = load_model_config()
        self.config = config
        self._providers: Dict[str, ModelProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize provider instances for each role"""
        for role_name, role_config in self.config.roles.items():
            provider_type = role_config.provider
            provider_config = self.config.providers.get(provider_type, {})
            
            provider = create_provider(provider_type, role_config, provider_config)
            self._providers[role_name] = provider
    
    def get_model(self, role: str) -> ModelProvider:
        """
        Get model provider for a specific role.
        
        Args:
            role: Role name (reasoning_model, classification_model, generation_model)
            
        Returns:
            ModelProvider instance for the role
            
        Raises:
            KeyError: If role is not configured
        """
        if role not in self._providers:
            raise KeyError(f"Role '{role}' not configured. Available roles: {list(self._providers.keys())}")
        
        return self._providers[role]
    
    async def reasoning(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Use reasoning model for multi-step security analysis.
        
        Args:
            prompt: User prompt/question
            context: Additional context (evidence, findings, etc.)
            **kwargs: Additional parameters
            
        Returns:
            Response dict with 'content' and metadata
        """
        model = self.get_model("reasoning_model")
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        # Add context to messages if provided
        if context:
            context_str = self._format_context(context)
            messages.append({"role": "user", "content": f"Context: {context_str}"})
        
        role_config = get_role_config(self.config, "reasoning_model")
        
        return await model.chat_completion(
            messages=messages,
            system_prompt=role_config.system_prompt,
            parameters=role_config.parameters,
            **kwargs
        )
    
    async def classify(
        self,
        evidence: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Use classification model to map evidence to controls/domains.
        
        Args:
            evidence: Evidence dict (from Bronze or Silver layer)
            **kwargs: Additional parameters
            
        Returns:
            Classification result with control_id, domain_code, confidence_score
        """
        model = self.get_model("classification_model")
        
        # Format evidence for classification
        evidence_str = self._format_evidence(evidence)
        
        prompt = f"""
        Classify the following security evidence to the appropriate control and domain.
        Return JSON with: control_id, domain_code, confidence_score.
        
        Evidence:
        {evidence_str}
        """
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        role_config = get_role_config(self.config, "classification_model")
        
        response = await model.chat_completion(
            messages=messages,
            system_prompt=role_config.system_prompt,
            parameters=role_config.parameters,
            **kwargs
        )
        
        # Parse JSON response
        import json
        try:
            content = response["content"]
            # Extract JSON from response (might be wrapped in markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            classification = json.loads(content)
            return {
                "classification": classification,
                "raw_response": response,
            }
        except json.JSONDecodeError:
            # If JSON parsing fails, return raw response
            return {
                "classification": None,
                "raw_response": response,
                "error": "Failed to parse JSON response",
            }
    
    async def generate(
        self,
        section_type: str,
        data: Dict[str, Any],
        template: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Use generation model to write report sections.
        
        Args:
            section_type: Type of section (executive_summary, findings, recommendations, etc.)
            data: Data to include in the section
            template: Optional template/formatting instructions
            **kwargs: Additional parameters
            
        Returns:
            Generated content dict with 'content' and metadata
        """
        model = self.get_model("generation_model")
        
        # Format data for generation
        data_str = self._format_data(data)
        
        prompt = f"""
        Generate a {section_type} section for a security assessment report.
        
        Data:
        {data_str}
        
        {f"Template/Format: {template}" if template else ""}
        
        Generate clear, professional, executive-level content suitable for a consulting report.
        """
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        role_config = get_role_config(self.config, "generation_model")
        
        return await model.chat_completion(
            messages=messages,
            system_prompt=role_config.system_prompt,
            parameters=role_config.parameters,
            **kwargs
        )
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dict as string"""
        import json
        return json.dumps(context, indent=2)
    
    def _format_evidence(self, evidence: Dict[str, Any]) -> str:
        """Format evidence dict as string"""
        import json
        return json.dumps(evidence, indent=2)
    
    def _format_data(self, data: Dict[str, Any]) -> str:
        """Format data dict as string"""
        import json
        return json.dumps(data, indent=2)


# Global Model Layer instance (singleton pattern)
_model_layer: Optional[ModelLayer] = None


def get_model(role: Optional[str] = None) -> ModelProvider:
    """
    Get model provider for a specific role.
    
    Args:
        role: Role name (reasoning_model, classification_model, generation_model).
              If None, returns the ModelLayer instance.
              
    Returns:
        ModelProvider for the role, or ModelLayer instance if role is None
    """
    global _model_layer
    
    if _model_layer is None:
        _model_layer = ModelLayer()
    
    if role is None:
        return _model_layer
    
    return _model_layer.get_model(role)


def get_model_layer() -> ModelLayer:
    """
    Get the global ModelLayer instance.
    
    Returns:
        ModelLayer instance
    """
    global _model_layer
    
    if _model_layer is None:
        _model_layer = ModelLayer()
    
    return _model_layer

