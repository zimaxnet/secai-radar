"""
SecAI Radar API Utilities

Common utilities for Azure Table Storage, Blob Storage, and HTTP responses.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

from azure.core.exceptions import ResourceExistsError
from azure.data.tables import TableServiceClient
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)

# Environment configuration
TENANT_ID = os.getenv("TENANT_ID", "NICO")
TABLES_CONN = os.getenv("TABLES_CONN")
BLOBS_CONN = os.getenv("BLOBS_CONN")
BLOB_CONTAINER = os.getenv("BLOB_CONTAINER", "assessments")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")


def cors_headers(origin: Optional[str] = None) -> Dict[str, str]:
    """
    Generate CORS headers for HTTP responses.
    
    Args:
        origin: Optional specific origin to allow. If not provided, uses ALLOWED_ORIGINS env var.
        
    Returns:
        Dict of CORS headers.
    """
    return {
        "Access-Control-Allow-Origin": origin or ALLOWED_ORIGINS,
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        "Access-Control-Max-Age": "86400",
    }


def table_client(table_name: str):
    """
    Get or create an Azure Table Storage client.
    
    Args:
        table_name: Name of the table to access.
        
    Returns:
        TableClient for the specified table.
        
    Raises:
        ValueError: If TABLES_CONN environment variable is not set.
    """
    if not TABLES_CONN:
        raise ValueError("TABLES_CONN environment variable is not set")
    
    svc = TableServiceClient.from_connection_string(TABLES_CONN)
    try:
        svc.create_table_if_not_exists(table_name=table_name)
    except ResourceExistsError:
        pass  # Table already exists, which is fine
    except Exception as e:
        logger.warning("Could not create table %s: %s", table_name, e)
    
    return svc.get_table_client(table_name)


def blob_container():
    """
    Get or create an Azure Blob Storage container client.
    
    Returns:
        ContainerClient for the configured container.
        
    Raises:
        ValueError: If BLOBS_CONN environment variable is not set.
    """
    if not BLOBS_CONN:
        raise ValueError("BLOBS_CONN environment variable is not set")
    
    svc = BlobServiceClient.from_connection_string(BLOBS_CONN)
    try:
        svc.create_container(BLOB_CONTAINER)
    except ResourceExistsError:
        pass  # Container already exists, which is fine
    except Exception as e:
        logger.warning("Could not create container %s: %s", BLOB_CONTAINER, e)
    
    return svc.get_container_client(BLOB_CONTAINER)


def json_response(data: Any, status: int = 200, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Create a standardized JSON HTTP response.
    
    Args:
        data: Data to serialize as JSON.
        status: HTTP status code (default: 200).
        headers: Optional additional headers to include.
        
    Returns:
        Dict suitable for azure.functions.HttpResponse constructor.
    """
    response_headers = cors_headers()
    if headers:
        response_headers.update(headers)
    
    return {
        "status_code": status,
        "mimetype": "application/json",
        "headers": response_headers,
        "body": json.dumps(data, default=str),
    }
