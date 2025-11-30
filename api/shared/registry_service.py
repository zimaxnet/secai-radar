"""
Agent Registry Service

Centralized registry for all AI agents in SecAI Radar.
Provides single source of truth for agent inventory, discoverability, and governance.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from shared.utils import table_client

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent status values"""
    ACTIVE = "active"
    IDLE = "idle"
    QUARANTINED = "quarantined"
    DISABLED = "disabled"
    ERROR = "error"


@dataclass
class AgentRegistryEntry:
    """Registry entry for an agent"""
    agent_id: str
    entra_agent_id: Optional[str]
    name: str
    role: str
    status: str  # AgentStatus
    blueprint: str
    capabilities: List[str]
    collections: List[str]
    last_active_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]


class RegistryService:
    """
    Service for managing the agent registry.
    
    Provides:
    - Agent inventory and discovery
    - Collection management (quarantine, custom collections)
    - Agent status tracking
    - Third-party agent registration
    """
    
    def __init__(self, table_name: str = "AgentRegistry"):
        """
        Initialize the registry service.
        
        Args:
            table_name: Azure Table Storage table name for registry
        """
        self.table_name = table_name
        self._table_client = None
    
    @property
    def table_client(self):
        """Lazy-load table client"""
        if self._table_client is None:
            self._table_client = table_client(self.table_name)
        return self._table_client
    
    def register_agent(
        self,
        agent_id: str,
        entra_agent_id: Optional[str],
        name: str,
        role: str,
        blueprint: str,
        capabilities: List[str],
        collections: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentRegistryEntry:
        """
        Register an agent in the registry.
        
        Args:
            agent_id: Unique agent identifier
            entra_agent_id: Entra Agent ID (service principal object ID)
            name: Agent display name
            role: Agent role/title
            blueprint: Agent blueprint identifier
            capabilities: List of agent capabilities
            collections: Optional list of collection names (defaults to ["secai-core"])
            metadata: Optional additional metadata
            
        Returns:
            AgentRegistryEntry
        """
        now = datetime.utcnow()
        
        entry = AgentRegistryEntry(
            agent_id=agent_id,
            entra_agent_id=entra_agent_id,
            name=name,
            role=role,
            status=AgentStatus.ACTIVE.value,
            blueprint=blueprint,
            capabilities=capabilities or [],
            collections=collections or ["secai-core"],
            last_active_at=now,
            created_at=now,
            updated_at=now,
            metadata=metadata or {}
        )
        
        # Store in Table Storage
        entity = {
            "PartitionKey": "agents",
            "RowKey": agent_id,
            "entra_agent_id": entra_agent_id or "",
            "name": name,
            "role": role,
            "status": entry.status,
            "blueprint": blueprint,
            "capabilities": ",".join(capabilities) if capabilities else "",
            "collections": ",".join(entry.collections),
            "last_active_at": now.isoformat() if now else "",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "metadata": str(metadata) if metadata else ""
        }
        
        try:
            self.table_client.upsert_entity(entity)
            logger.info(f"Registered agent in registry: {agent_id}")
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
            raise
        
        return entry
    
    def get_agent(self, agent_id: str) -> Optional[AgentRegistryEntry]:
        """
        Get an agent from the registry.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            AgentRegistryEntry or None if not found
        """
        try:
            entity = self.table_client.get_entity(partition_key="agents", row_key=agent_id)
            return self._entity_to_entry(entity)
        except Exception as e:
            logger.debug(f"Agent {agent_id} not found in registry: {e}")
            return None
    
    def list_agents(
        self,
        status: Optional[str] = None,
        collection: Optional[str] = None,
        blueprint: Optional[str] = None,
        capability: Optional[str] = None
    ) -> List[AgentRegistryEntry]:
        """
        List agents with optional filtering.
        
        Args:
            status: Filter by status (active, quarantined, etc.)
            collection: Filter by collection name
            blueprint: Filter by blueprint
            capability: Filter by capability
            
        Returns:
            List of AgentRegistryEntry
        """
        try:
            # Query all agents
            entities = self.table_client.query_entities(
                query_filter="PartitionKey eq 'agents'"
            )
            
            entries = []
            for entity in entities:
                entry = self._entity_to_entry(entity)
                
                # Apply filters
                if status and entry.status != status:
                    continue
                if collection and collection not in entry.collections:
                    continue
                if blueprint and entry.blueprint != blueprint:
                    continue
                if capability and capability not in entry.capabilities:
                    continue
                
                entries.append(entry)
            
            return entries
        except Exception as e:
            logger.error(f"Failed to list agents: {e}")
            return []
    
    def update_agent_status(
        self,
        agent_id: str,
        status: str
    ) -> bool:
        """
        Update an agent's status.
        
        Args:
            agent_id: Agent identifier
            status: New status (active, quarantined, disabled, etc.)
            
        Returns:
            True if updated successfully
        """
        try:
            entity = self.table_client.get_entity(partition_key="agents", row_key=agent_id)
            entity["status"] = status
            entity["updated_at"] = datetime.utcnow().isoformat()
            self.table_client.update_entity(entity)
            logger.info(f"Updated agent {agent_id} status to {status}")
            return True
        except Exception as e:
            logger.error(f"Failed to update agent {agent_id} status: {e}")
            return False
    
    def add_to_collection(
        self,
        agent_id: str,
        collection_name: str
    ) -> bool:
        """
        Add an agent to a collection.
        
        Args:
            agent_id: Agent identifier
            collection_name: Collection name
            
        Returns:
            True if added successfully
        """
        try:
            entity = self.table_client.get_entity(partition_key="agents", row_key=agent_id)
            collections = entity.get("collections", "").split(",")
            collections = [c.strip() for c in collections if c.strip()]
            
            if collection_name not in collections:
                collections.append(collection_name)
                entity["collections"] = ",".join(collections)
                entity["updated_at"] = datetime.utcnow().isoformat()
                self.table_client.update_entity(entity)
                logger.info(f"Added agent {agent_id} to collection {collection_name}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to add agent {agent_id} to collection: {e}")
            return False
    
    def remove_from_collection(
        self,
        agent_id: str,
        collection_name: str
    ) -> bool:
        """
        Remove an agent from a collection.
        
        Args:
            agent_id: Agent identifier
            collection_name: Collection name
            
        Returns:
            True if removed successfully
        """
        try:
            entity = self.table_client.get_entity(partition_key="agents", row_key=agent_id)
            collections = entity.get("collections", "").split(",")
            collections = [c.strip() for c in collections if c.strip()]
            
            if collection_name in collections:
                collections.remove(collection_name)
                entity["collections"] = ",".join(collections)
                entity["updated_at"] = datetime.utcnow().isoformat()
                self.table_client.update_entity(entity)
                logger.info(f"Removed agent {agent_id} from collection {collection_name}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to remove agent {agent_id} from collection: {e}")
            return False
    
    def quarantine_agent(self, agent_id: str) -> bool:
        """
        Quarantine an agent (add to quarantine collection and set status).
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if quarantined successfully
        """
        success = self.update_agent_status(agent_id, AgentStatus.QUARANTINED.value)
        if success:
            self.add_to_collection(agent_id, "quarantine")
        return success
    
    def unquarantine_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from quarantine.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if unquarantined successfully
        """
        success = self.update_agent_status(agent_id, AgentStatus.ACTIVE.value)
        if success:
            self.remove_from_collection(agent_id, "quarantine")
        return success
    
    def update_last_active(self, agent_id: str) -> None:
        """
        Update the last active timestamp for an agent.
        
        Args:
            agent_id: Agent identifier
        """
        try:
            entity = self.table_client.get_entity(partition_key="agents", row_key=agent_id)
            entity["last_active_at"] = datetime.utcnow().isoformat()
            entity["updated_at"] = datetime.utcnow().isoformat()
            self.table_client.update_entity(entity)
        except Exception as e:
            logger.debug(f"Could not update last active for agent {agent_id}: {e}")
    
    def _entity_to_entry(self, entity: Dict[str, Any]) -> AgentRegistryEntry:
        """Convert Table Storage entity to AgentRegistryEntry"""
        capabilities = entity.get("capabilities", "").split(",")
        capabilities = [c.strip() for c in capabilities if c.strip()]
        
        collections = entity.get("collections", "").split(",")
        collections = [c.strip() for c in collections if c.strip()]
        
        created_at = datetime.fromisoformat(entity.get("created_at", datetime.utcnow().isoformat()))
        updated_at = datetime.fromisoformat(entity.get("updated_at", datetime.utcnow().isoformat()))
        last_active_at = None
        if entity.get("last_active_at"):
            try:
                last_active_at = datetime.fromisoformat(entity["last_active_at"])
            except:
                pass
        
        # Parse metadata (stored as string)
        metadata = {}
        if entity.get("metadata"):
            try:
                import ast
                metadata = ast.literal_eval(entity["metadata"])
            except:
                pass
        
        return AgentRegistryEntry(
            agent_id=entity["RowKey"],
            entra_agent_id=entity.get("entra_agent_id") or None,
            name=entity.get("name", ""),
            role=entity.get("role", ""),
            status=entity.get("status", AgentStatus.ACTIVE.value),
            blueprint=entity.get("blueprint", ""),
            capabilities=capabilities,
            collections=collections,
            last_active_at=last_active_at,
            created_at=created_at,
            updated_at=updated_at,
            metadata=metadata
        )


# Singleton instance
_registry_service: Optional[RegistryService] = None


def get_registry_service() -> RegistryService:
    """Get or create the registry service instance"""
    global _registry_service
    if _registry_service is None:
        _registry_service = RegistryService()
    return _registry_service

