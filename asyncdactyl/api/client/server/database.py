from typing import Dict, Any
from dataclasses import dataclass

from ....exceptions import OperationFailed
from ....objects import BasePteroObject, Relationships


@dataclass
class DatabaseHost:
    adress: str
    port: int

class ClientServerDatabaseAPI:
    def __init__(self, id: str, server_id: str, client):
        self.client = client
        self.server_id = server_id
        self.id = id

    async def fetch(self) -> "ClientServerDatabase":
        server = await self.client._client.get_server(self.server_id, fetch=False)
        return await server.get_database(self.id)
        
    async def rotate_password(self) -> DatabaseHost:
        endpoint = f"/servers/{self.server_id}/databases/{self.id}/rotate-pasword"
        result = await self.client.api_request(endpoint, method="POST", json=False)
        if (status := result.status) != 200:
            raise OperationFailed(200, status)
        return ClientServerDatabase(result, self.id, self.client)
    
    async def delete(self) -> None:
        endpoint = f"/servers/{self.server_id}/databases/{self.id}"
        result = await self.client.api_request(endpoint, method="DELETE", json=False)
        if (status := result.status) != 204:
            raise OperationFailed(204, status)

class ClientServerDatabase(BasePteroObject, ClientServerDatabaseAPI):
    def __init__(self, data: Dict[str, Any], server_id: str, client):
        super().__init__(data)
        self.server_id = server_id
        self.client = client
        
        data = data["attributes"]
        self.id: str = data["id"]
        self.host = DatabaseHost(**data["host"])
        self.name: str = data["name"]
        self.username: str = data["username"]
        self.connections_from: str = data["connections_from"]
        self.max_connections: int = data["max_connections"]
        self.relationships = Relationships(data.get("relationships", {}))

    @property
    def password(self):
        return self.relationships.password