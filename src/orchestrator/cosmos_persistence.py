"""
Azure Cosmos DB State Persistence

Implements state persistence using Azure Cosmos DB for multi-agent orchestration.
"""

import os
from typing import Optional, Dict, Any
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from .state import AssessmentState, StateManager


class CosmosStatePersistence:
    """
    Cosmos DB implementation for state persistence.
    """
    
    def __init__(
        self,
        cosmos_endpoint: Optional[str] = None,
        cosmos_key: Optional[str] = None,
        database_name: str = "secai_radar",
        container_name: str = "assessment_states"
    ):
        """
        Initialize Cosmos DB persistence.
        
        Args:
            cosmos_endpoint: Cosmos DB endpoint URL (or set COSMOS_ENDPOINT env var)
            cosmos_key: Cosmos DB key (or set COSMOS_KEY env var)
            database_name: Database name
            container_name: Container name
        """
        self.cosmos_endpoint = cosmos_endpoint or os.getenv("COSMOS_ENDPOINT")
        self.cosmos_key = cosmos_key or os.getenv("COSMOS_KEY")
        self.database_name = database_name
        self.container_name = container_name
        
        self.client = None
        self.database = None
        self.container = None
        
        if self.cosmos_endpoint and self.cosmos_key:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Cosmos DB client and create database/container if needed"""
        try:
            self.client = CosmosClient(
                self.cosmos_endpoint,
                self.cosmos_key
            )
            
            # Create database if it doesn't exist
            try:
                self.database = self.client.get_database_client(self.database_name)
                self.database.read()
            except CosmosResourceNotFoundError:
                self.database = self.client.create_database(
                    id=self.database_name
                )
            
            # Create container if it doesn't exist
            try:
                self.container = self.database.get_container_client(self.container_name)
                self.container.read()
            except CosmosResourceNotFoundError:
                self.container = self.database.create_container(
                    id=self.container_name,
                    partition_key=PartitionKey(path="/assessment_id"),
                    offer_throughput=400
                )
        except Exception as e:
            print(f"Error initializing Cosmos DB client: {e}")
            self.client = None
    
    def persist_state(
        self,
        state: AssessmentState,
        state_manager: StateManager
    ) -> bool:
        """
        Persist assessment state to Cosmos DB.
        
        Note: Cosmos DB SDK is synchronous, but this method can be called
        from async contexts using asyncio.to_thread() if needed.
        
        Args:
            state: Assessment state to persist
            state_manager: StateManager instance for conversion
            
        Returns:
            True if successful
        """
        if not self.container:
            return False
        
        try:
            # Convert state to dict
            state_dict = state_manager._state_to_dict(state)
            
            # Ensure assessment_id is the id field for Cosmos DB
            state_dict["id"] = state["assessment_id"]
            
            # Upsert to Cosmos DB (synchronous operation)
            self.container.upsert_item(state_dict)
            return True
        except Exception as e:
            print(f"Error persisting state to Cosmos DB: {e}")
            return False
    
    def load_state(
        self,
        assessment_id: str,
        state_manager: StateManager
    ) -> Optional[AssessmentState]:
        """
        Load assessment state from Cosmos DB.
        
        Note: Cosmos DB SDK is synchronous, but this method can be called
        from async contexts using asyncio.to_thread() if needed.
        
        Args:
            assessment_id: Assessment identifier
            state_manager: StateManager instance for conversion
            
        Returns:
            AssessmentState if found, None otherwise
        """
        if not self.container:
            return None
        
        try:
            # Read item from Cosmos DB (synchronous operation)
            item = self.container.read_item(
                item=assessment_id,
                partition_key=assessment_id
            )
            
            # Convert dict back to state
            return state_manager._dict_to_state(item)
        except CosmosResourceNotFoundError:
            return None
        except Exception as e:
            print(f"Error loading state from Cosmos DB: {e}")
            return None
    
    def list_assessments(
        self,
        tenant_id: Optional[str] = None
    ) -> list[Dict[str, Any]]:
        """
        List all assessments (optionally filtered by tenant).
        
        Args:
            tenant_id: Optional tenant ID filter
            
        Returns:
            List of assessment metadata
        """
        if not self.container:
            return []
        
        try:
            query = "SELECT c.assessment_id, c.tenant_id, c.phase, c.created_at, c.updated_at FROM c"
            if tenant_id:
                query += f" WHERE c.tenant_id = '{tenant_id}'"
            query += " ORDER BY c.updated_at DESC"
            
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=not tenant_id
            ))
            
            return items
        except Exception as e:
            print(f"Error listing assessments: {e}")
            return []
    
    def delete_state(self, assessment_id: str) -> bool:
        """
        Delete assessment state from Cosmos DB.
        
        Args:
            assessment_id: Assessment identifier
            
        Returns:
            True if successful
        """
        if not self.container:
            return False
        
        try:
            self.container.delete_item(
                item=assessment_id,
                partition_key=assessment_id
            )
            return True
        except CosmosResourceNotFoundError:
            return True  # Already deleted
        except Exception as e:
            print(f"Error deleting state from Cosmos DB: {e}")
            return False

