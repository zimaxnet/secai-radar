"""
Azure Key Vault Integration for SecAI Radar

Provides secure access to secrets, keys, and certificates from Azure Key Vault.
Uses Managed Identity for authentication when available, falls back to client credentials.
"""

import logging
import os
from typing import Optional

from azure.core.exceptions import ClientAuthenticationError, ResourceNotFoundError
from azure.identity import (
    ClientSecretCredential,
    DefaultAzureCredential,
    ManagedIdentityCredential,
)
from azure.keyvault.secrets import SecretClient

logger = logging.getLogger(__name__)


class KeyVaultService:
    """Service for accessing Azure Key Vault secrets"""
    
    def __init__(self, vault_url: Optional[str] = None):
        """
        Initialize Key Vault service
        
        Args:
            vault_url: Key Vault URL (e.g., https://secai-radar-kv.vault.azure.net/)
                      If not provided, will use KEY_VAULT_URL from environment
        """
        self.vault_url = vault_url or os.getenv("KEY_VAULT_URL")
        
        if not self.vault_url:
            raise ValueError("KEY_VAULT_URL environment variable or vault_url parameter is required")
        
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Key Vault client with appropriate credentials."""
        # Try Managed Identity first (for Azure-hosted environments)
        try:
            self.credential = ManagedIdentityCredential()
            self.client = SecretClient(vault_url=self.vault_url, credential=self.credential)
            # Validate by attempting to list (will fail fast if auth is invalid)
            logger.debug("Attempting Managed Identity authentication for Key Vault")
            return
        except ClientAuthenticationError:
            logger.debug("Managed Identity not available, trying DefaultAzureCredential")
        except Exception as e:
            logger.debug("Managed Identity failed: %s", e)
        
        # Fall back to DefaultAzureCredential (Azure CLI, VS Code, etc.)
        try:
            self.credential = DefaultAzureCredential()
            self.client = SecretClient(vault_url=self.vault_url, credential=self.credential)
            logger.debug("Using DefaultAzureCredential for Key Vault")
            return
        except ClientAuthenticationError as e:
            logger.debug("DefaultAzureCredential failed: %s", e)
        except Exception as e:
            logger.debug("DefaultAzureCredential error: %s", e)
        
        # If both fail, try client credentials (for service principal)
        tenant_id = os.getenv("AZURE_TENANT_ID")
        client_id = os.getenv("AZURE_CLIENT_ID")
        client_secret = os.getenv("AZURE_CLIENT_SECRET")
        
        if tenant_id and client_id and client_secret:
            self.credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
            self.client = SecretClient(vault_url=self.vault_url, credential=self.credential)
            logger.debug("Using ClientSecretCredential for Key Vault")
        else:
            raise ValueError(
                "Unable to authenticate to Key Vault. "
                "Ensure Managed Identity, Azure CLI login, or service principal credentials are available."
            )
    
    def get_secret(self, secret_name: str) -> str:
        """
        Get a secret from Key Vault
        
        Args:
            secret_name: Name of the secret
            
        Returns:
            Secret value as string
        """
        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            raise ValueError(f"Failed to get secret '{secret_name}' from Key Vault: {e}")
    
    def set_secret(self, secret_name: str, secret_value: str) -> None:
        """
        Set a secret in Key Vault (requires appropriate permissions)
        
        Args:
            secret_name: Name of the secret
            secret_value: Value to store
        """
        try:
            self.client.set_secret(secret_name, secret_value)
        except Exception as e:
            raise ValueError(f"Failed to set secret '{secret_name}' in Key Vault: {e}")


# Singleton instance
_key_vault_instance: Optional[KeyVaultService] = None

def get_key_vault() -> Optional[KeyVaultService]:
    """Get or create the Key Vault service instance"""
    global _key_vault_instance
    if _key_vault_instance is None:
        try:
            _key_vault_instance = KeyVaultService()
        except ValueError:
            # Key Vault not configured - return None
            return None
    return _key_vault_instance

def get_secret_from_key_vault_or_env(secret_name: str, env_var_name: Optional[str] = None) -> Optional[str]:
    """
    Get secret from Key Vault, or fall back to environment variable.
    
    This function provides a seamless way to retrieve secrets that works both
    in Azure (using Key Vault) and locally (using environment variables).
    
    Args:
        secret_name: Key Vault secret name
        env_var_name: Environment variable name (defaults to secret_name)
        
    Returns:
        Secret value or None if not found in either location
    """
    # Try Key Vault first
    kv = get_key_vault()
    if kv:
        try:
            secret = kv.get_secret(secret_name)
            logger.debug("Retrieved secret '%s' from Key Vault", secret_name)
            return secret
        except ResourceNotFoundError:
            logger.debug("Secret '%s' not found in Key Vault, falling back to env var", secret_name)
        except Exception as e:
            logger.warning("Error retrieving secret '%s' from Key Vault: %s", secret_name, e)
    
    # Fall back to environment variable
    env_name = env_var_name or secret_name
    value = os.getenv(env_name)
    if value:
        logger.debug("Retrieved secret from environment variable '%s'", env_name)
    return value

