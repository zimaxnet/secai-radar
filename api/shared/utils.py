
import os, json
from azure.data.tables import TableServiceClient
from azure.storage.blob import BlobServiceClient

TENANT_ID = os.getenv("TENANT_ID", "NICO")
TABLES_CONN = os.getenv("TABLES_CONN")
BLOBS_CONN = os.getenv("BLOBS_CONN")
BLOB_CONTAINER = os.getenv("BLOB_CONTAINER", "assessments")

def table_client(table_name: str):
    svc = TableServiceClient.from_connection_string(TABLES_CONN)
    try: svc.create_table_if_not_exists(table_name=table_name)
    except Exception: pass
    return svc.get_table_client(table_name)

def blob_container():
    svc = BlobServiceClient.from_connection_string(BLOBS_CONN)
    try: svc.create_container(BLOB_CONTAINER)
    except Exception: pass
    return svc.get_container_client(BLOB_CONTAINER)

def json_response(data, status=200):
    return {"status_code": status, "mimetype": "application/json", "body": json.dumps(data, default=str)}
