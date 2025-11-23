"""
Azure Storage Services
Provides table and blob storage clients for controls, tools, and evidence
"""

import os
from typing import Optional
from azure.data.tables import TableServiceClient, TableClient
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.core.exceptions import ResourceExistsError

# Environment variables
TABLES_CONN_STR = os.getenv("TABLES_CONN")
BLOBS_CONN_STR = os.getenv("BLOBS_CONN")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER", "assessments")

# Table names
CONTROLS_TABLE = "Controls"
TENANT_TOOLS_TABLE = "TenantTools"


class StorageService:
    """Centralized storage service for Azure Table and Blob storage"""
    
    def __init__(self):
        self._table_service: Optional[TableServiceClient] = None
        self._blob_service: Optional[BlobServiceClient] = None
        self._initialized_tables = set()
    
    def get_table_client(self, table_name: str) -> TableClient:
        """Get or create a table client"""
        if not TABLES_CONN_STR:
            raise ValueError("TABLES_CONN environment variable is not set")
        
        if not self._table_service:
            self._table_service = TableServiceClient.from_connection_string(TABLES_CONN_STR)
        
        # Create table if it doesn't exist (only once per table)
        if table_name not in self._initialized_tables:
            try:
                self._table_service.create_table_if_not_exists(table_name=table_name)
                self._initialized_tables.add(table_name)
            except ResourceExistsError:
                self._initialized_tables.add(table_name)
            except Exception as e:
                # Table might already exist, continue
                self._initialized_tables.add(table_name)
        
        return self._table_service.get_table_client(table_name)
    
    def get_blob_container(self) -> ContainerClient:
        """Get or create a blob container client"""
        if not BLOBS_CONN_STR:
            raise ValueError("BLOBS_CONN environment variable is not set")
        
        if not self._blob_service:
            self._blob_service = BlobServiceClient.from_connection_string(BLOBS_CONN_STR)
        
        try:
            self._blob_service.create_container(BLOB_CONTAINER_NAME)
        except ResourceExistsError:
            pass
        except Exception:
            pass
        
        return self._blob_service.get_container_client(BLOB_CONTAINER_NAME)
    
    def get_controls_table(self) -> TableClient:
        """Get the controls table client"""
        return self.get_table_client(CONTROLS_TABLE)
    
    def get_tenant_tools_table(self) -> TableClient:
        """Get the tenant tools table client"""
        return self.get_table_client(TENANT_TOOLS_TABLE)


# Singleton instance
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get or create the storage service instance"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service

