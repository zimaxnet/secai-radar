"""
Agent Identity Service

Manages Entra Agent IDs for SecAI Radar agents, providing:
- Agent identity provisioning and registration
- Token acquisition for agent authentication
- Identity validation and auditing
- Integration with Microsoft Graph API
"""

import os
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
    from azure.keyvault.secrets import SecretClient
    from azure.core.credentials import TokenCredential
    AZURE_IDENTITY_AVAILABLE = True
except ImportError:
    AZURE_IDENTITY_AVAILABLE = False
    DefaultAzureCredential = None
    ManagedIdentityCredential = None

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class AgentIdentity:
    """Represents an agent's Entra identity"""
    agent_id: str
    entra_agent_id: Optional[str]  # Service principal object ID
    app_id: Optional[str]  # Application (client) ID
    blueprint_id: str
    display_name: str
    status: str  # active, disabled, quarantined
    created_at: datetime
    last_validated_at: Optional[datetime] = None


class AgentIdentityService:
    """
    Service for managing Entra Agent IDs for SecAI Radar agents.
    
    Provides identity lifecycle management, token acquisition, and auditing.
    """
    
    def __init__(
        self,
        tenant_id: Optional[str] = None,
        credential: Optional[Any] = None,
        key_vault_url: Optional[str] = None
    ):
        """
        Initialize the Agent Identity Service.
        
        Args:
            tenant_id: Azure AD tenant ID (defaults to env var)
            credential: Azure credential (defaults to DefaultAzureCredential)
            key_vault_url: Key Vault URL for storing agent secrets
        """
        self.tenant_id = tenant_id or os.getenv("AZURE_TENANT_ID")
        self.key_vault_url = key_vault_url or os.getenv("AZURE_KEY_VAULT_URL")
        
        # Initialize credential
        if credential:
            self.credential = credential
        elif AZURE_IDENTITY_AVAILABLE:
            try:
                self.credential = DefaultAzureCredential()
            except Exception as e:
                logger.warning(f"Could not initialize DefaultAzureCredential: {e}")
                self.credential = None
        else:
            self.credential = None
        
        # Initialize Key Vault client if available
        self.key_vault_client = None
        if self.key_vault_url and AZURE_IDENTITY_AVAILABLE and self.credential:
            try:
                from azure.keyvault.secrets import SecretClient
                self.key_vault_client = SecretClient(
                    vault_url=self.key_vault_url,
                    credential=self.credential
                )
            except Exception as e:
                logger.warning(f"Could not initialize Key Vault client: {e}")
        
        # Cache for agent tokens
        self._token_cache: Dict[str, tuple[str, datetime]] = {}
        
        # Graph API endpoint
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
    
    def register_agent(
        self,
        agent_id: str,
        blueprint_id: str,
        display_name: str,
        description: Optional[str] = None
    ) -> AgentIdentity:
        """
        Register an agent with Entra ID and create a service principal.
        
        This creates an app registration and service principal for the agent,
        enabling it to authenticate and access resources.
        
        Args:
            agent_id: Unique agent identifier (e.g., "aris-thorne")
            blueprint_id: Agent blueprint identifier (e.g., "secai-assessment-agent")
            display_name: Human-readable agent name
            description: Optional agent description
            
        Returns:
            AgentIdentity with entra_agent_id and app_id populated
            
        Note:
            In production, this should use Microsoft Graph API to create
            app registrations. For now, we'll use a simplified approach
            that stores identity mappings in configuration.
        """
        # For preview/development, we'll use a simplified registration
        # In production, this would call Microsoft Graph API:
        # POST /applications
        # POST /servicePrincipals
        
        logger.info(f"Registering agent: {agent_id} with blueprint: {blueprint_id}")
        
        # Generate a mock Entra Agent ID (in production, this comes from Graph API)
        # Format: Use agent_id hash or retrieve from Graph API response
        entra_agent_id = self._generate_mock_entra_id(agent_id)
        app_id = self._generate_mock_app_id(agent_id)
        
        identity = AgentIdentity(
            agent_id=agent_id,
            entra_agent_id=entra_agent_id,
            app_id=app_id,
            blueprint_id=blueprint_id,
            display_name=display_name,
            status="active",
            created_at=datetime.utcnow()
        )
        
        # Store identity mapping (in production, persist to Cosmos DB or Table Storage)
        self._store_identity(identity)
        
        logger.info(f"Agent {agent_id} registered with Entra ID: {entra_agent_id}")
        return identity
    
    def get_agent_token(
        self,
        agent_id: str,
        scopes: Optional[list[str]] = None
    ) -> str:
        """
        Get an access token for an agent using its Entra Agent ID.
        
        Args:
            agent_id: Agent identifier
            scopes: Optional list of scopes (defaults to ["https://graph.microsoft.com/.default"])
            
        Returns:
            Access token string
            
        Raises:
            ValueError: If agent is not registered or token acquisition fails
        """
        if scopes is None:
            scopes = ["https://graph.microsoft.com/.default"]
        
        # Check cache first
        cache_key = f"{agent_id}:{':'.join(scopes)}"
        if cache_key in self._token_cache:
            token, expires_at = self._token_cache[cache_key]
            if expires_at > datetime.utcnow():
                return token
        
        # Load agent identity
        identity = self._load_identity(agent_id)
        if not identity:
            raise ValueError(f"Agent {agent_id} is not registered")
        
        if identity.status != "active":
            raise ValueError(f"Agent {agent_id} is not active (status: {identity.status})")
        
        # Acquire token using client credentials flow
        # In production, this uses the service principal's credentials
        token = self._acquire_token_for_agent(identity, scopes)
        
        # Cache token (expires in 1 hour typically)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        self._token_cache[cache_key] = (token, expires_at)
        
        return token
    
    def validate_agent_identity(self, agent_id: str) -> bool:
        """
        Validate that an agent's identity is still valid and active.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if identity is valid and active, False otherwise
        """
        identity = self._load_identity(agent_id)
        if not identity:
            return False
        
        # Check if identity is active
        if identity.status != "active":
            return False
        
        # In production, validate with Graph API:
        # GET /servicePrincipals/{id}
        # Check if service principal exists and is enabled
        
        # Update last validated timestamp
        identity.last_validated_at = datetime.utcnow()
        self._store_identity(identity)
        
        return True
    
    def audit_agent_action(
        self,
        agent_id: str,
        action: str,
        resource: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Audit an agent action for compliance and security monitoring.
        
        Args:
            agent_id: Agent identifier
            action: Action performed (e.g., "tool_call", "api_access")
            resource: Resource accessed (e.g., "storage_account", "api_endpoint")
            details: Optional additional details
        """
        identity = self._load_identity(agent_id)
        if not identity:
            logger.warning(f"Audit attempt for unregistered agent: {agent_id}")
            return
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "entra_agent_id": identity.entra_agent_id,
            "action": action,
            "resource": resource,
            "details": details or {}
        }
        
        # Log audit entry
        logger.info(f"Agent audit: {agent_id} -> {action} on {resource}")
        
        # In production, send to Application Insights or Log Analytics
        # This enables compliance reporting and security monitoring
    
    def _generate_mock_entra_id(self, agent_id: str) -> str:
        """Generate a mock Entra Agent ID for development"""
        import hashlib
        hash_obj = hashlib.sha256(agent_id.encode())
        # Format as GUID-like string
        hex_str = hash_obj.hexdigest()[:32]
        return f"{hex_str[:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}"
    
    def _generate_mock_app_id(self, agent_id: str) -> str:
        """Generate a mock App ID for development"""
        import hashlib
        hash_obj = hashlib.sha256(f"{agent_id}:app".encode())
        hex_str = hash_obj.hexdigest()[:32]
        return f"{hex_str[:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}"
    
    def _store_identity(self, identity: AgentIdentity) -> None:
        """Store agent identity (in-memory for now, should use Table Storage or Cosmos DB)"""
        # In production, persist to Azure Table Storage or Cosmos DB
        # For now, use a simple in-memory store
        if not hasattr(self, '_identity_store'):
            self._identity_store: Dict[str, AgentIdentity] = {}
        self._identity_store[identity.agent_id] = identity
    
    def _load_identity(self, agent_id: str) -> Optional[AgentIdentity]:
        """Load agent identity from storage"""
        if not hasattr(self, '_identity_store'):
            self._identity_store: Dict[str, AgentIdentity] = {}
        return self._identity_store.get(agent_id)
    
    def _acquire_token_for_agent(
        self,
        identity: AgentIdentity,
        scopes: list[str]
    ) -> str:
        """
        Acquire an access token for an agent using client credentials flow.
        
        In production, this would:
        1. Retrieve client secret from Key Vault
        2. Use MSAL or azure-identity to acquire token
        3. Return the access token
        """
        # For development, return a mock token
        # In production, use:
        # from azure.identity import ClientSecretCredential
        # credential = ClientSecretCredential(
        #     tenant_id=self.tenant_id,
        #     client_id=identity.app_id,
        #     client_secret=client_secret
        # )
        # token = credential.get_token(" ".join(scopes))
        
        logger.debug(f"Acquiring token for agent {identity.agent_id} with scopes: {scopes}")
        return f"mock_token_{identity.agent_id}_{datetime.utcnow().timestamp()}"


# Singleton instance
_agent_identity_service: Optional[AgentIdentityService] = None


def get_agent_identity_service() -> AgentIdentityService:
    """Get or create the agent identity service instance"""
    global _agent_identity_service
    if _agent_identity_service is None:
        _agent_identity_service = AgentIdentityService()
    return _agent_identity_service

