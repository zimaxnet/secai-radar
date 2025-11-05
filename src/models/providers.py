"""
Model Provider Implementations

Abstract base class and concrete implementations for different AI model providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI, AsyncAzureOpenAI


class ModelProvider(ABC):
    """Abstract base class for AI model providers"""
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        parameters: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion from model.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: System prompt for the model
            parameters: Model-specific parameters (temperature, max_tokens, etc.)
            **kwargs: Additional provider-specific arguments
            
        Returns:
            Response dict with 'content' and metadata
        """
        pass
    
    @abstractmethod
    def get_endpoint(self) -> str:
        """Get the model endpoint URL"""
        pass


class AzureOpenAIProvider(ModelProvider):
    """
    Azure OpenAI Service provider implementation.
    
    Supports both API key and Azure AD authentication.
    """
    
    def __init__(
        self,
        deployment: str,
        account: str,
        api_version: str = "2024-02-15-preview",
        auth_method: str = "azure_ad",
        api_key: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """
        Initialize Azure OpenAI provider.
        
        Args:
            deployment: Deployment name (e.g., "gpt-5-chat")
            account: Azure OpenAI account name
            api_version: API version to use
            auth_method: "azure_ad" or "api_key"
            api_key: API key (if using api_key auth)
            tenant_id: Tenant ID (if using service principal)
            client_id: Client ID (if using service principal)
            client_secret: Client secret (if using service principal)
        """
        self.deployment = deployment
        self.account = account
        self.api_version = api_version
        self.auth_method = auth_method
        self.endpoint = f"https://{account}.openai.azure.com"
        
        # Initialize client based on auth method
        if auth_method == "api_key":
            api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
            if not api_key:
                raise ValueError("AZURE_OPENAI_API_KEY not set and api_key not provided")
            credential = AzureKeyCredential(api_key)
            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=api_key,
                api_version=api_version,
            )
            self.async_client = AsyncAzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=api_key,
                api_version=api_version,
            )
        else:  # azure_ad
            # Use DefaultAzureCredential (supports managed identity, service principal, etc.)
            credential = DefaultAzureCredential()
            
            # Get token provider for Azure AD authentication
            token_provider = get_bearer_token_provider(
                credential,
                "https://cognitiveservices.azure.com/.default"
            )
            
            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                azure_ad_token_provider=token_provider,
                api_version=api_version,
            )
            self.async_client = AsyncAzureOpenAI(
                azure_endpoint=self.endpoint,
                azure_ad_token_provider=token_provider,
                api_version=api_version,
            )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        parameters: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using Azure OpenAI.
        
        Args:
            messages: List of message dicts
            system_prompt: System prompt
            parameters: Model parameters (temperature, max_tokens, etc.)
            **kwargs: Additional arguments
            
        Returns:
            Response dict with 'content' and metadata
        """
        # Build messages list with system prompt
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        # Call Azure OpenAI API
        response = await self.async_client.chat.completions.create(
            model=self.deployment,
            messages=full_messages,
            temperature=parameters.get("temperature", 0.7),
            max_tokens=parameters.get("max_tokens", 2000),
            top_p=parameters.get("top_p", 0.95),
            frequency_penalty=parameters.get("frequency_penalty", 0.0),
            presence_penalty=parameters.get("presence_penalty", 0.0),
            **kwargs
        )
        
        # Extract response content
        content = response.choices[0].message.content
        
        return {
            "content": content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "finish_reason": response.choices[0].finish_reason,
        }
    
    def get_endpoint(self) -> str:
        """Get the Azure OpenAI endpoint URL"""
        return self.endpoint
    
    def get_deployment(self) -> str:
        """Get the deployment name"""
        return self.deployment


def create_provider(provider_type: str, role_config, provider_config: Dict[str, Any]) -> ModelProvider:
    """
    Factory function to create appropriate provider instance.
    
    Args:
        provider_type: Provider type (e.g., "azure_openai")
        role_config: ModelRoleConfig for the role
        provider_config: Provider configuration from models.yaml
        
    Returns:
        ModelProvider instance
    """
    if provider_type == "azure_openai":
        auth_method = provider_config.get("auth_method", "azure_ad")
        
        return AzureOpenAIProvider(
            deployment=role_config.deployment,
            account=role_config.account,
            api_version=provider_config.get("api_version", "2024-02-15-preview"),
            auth_method=auth_method,
            api_key=os.getenv("AZURE_OPENAI_API_KEY") if auth_method == "api_key" else None,
            tenant_id=role_config.tenant_id,
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")

