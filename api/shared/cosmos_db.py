import os
from azure.cosmos import CosmosClient, PartitionKey
from typing import Optional

class CosmosDBService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CosmosDBService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
        self.database_name = os.getenv("AZURE_COSMOS_DATABASE_NAME", "SecAIRadarDB")
        self.client = None
        self.database = None
        self.users_container = None
        self.credentials_container = None

        if self.connection_string:
            try:
                self.client = CosmosClient.from_connection_string(self.connection_string)
                self.database = self.client.create_database_if_not_exists(id=self.database_name)
                
                # Container for Users
                self.users_container = self.database.create_container_if_not_exists(
                    id="Users",
                    partition_key=PartitionKey(path="/username"),
                    offer_throughput=400
                )
                
                # Container for WebAuthn Credentials
                self.credentials_container = self.database.create_container_if_not_exists(
                    id="Credentials",
                    partition_key=PartitionKey(path="/user_id"),
                    offer_throughput=400
                )
            except Exception as e:
                print(f"Failed to initialize Cosmos DB: {e}")

    def get_users_container(self):
        return self.users_container

    def get_credentials_container(self):
        return self.credentials_container

# Global instance
cosmos_service = CosmosDBService()
