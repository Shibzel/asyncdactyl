from typing import Dict, Any

from ...exceptions import OperationFailed
from ..baseobject import BasePteroObject
from ..relationships import Relationships


@dataclass
class DatabaseHost:
    adress: str
    port: int

class ServerDatabaseClient:
    def __init__(self, server_id: str, id: str, client):
        self._client = client
        self.server_id = server_id
        self.id = id
        
    async def rotate_password(self) -> DatabaseHost:
        endpoint = f"/servers/{self.server_id}/databases/{self.id}/rotate-pasword"
        result = await self._client.api_request(endpoint, method="POST", json=False)
        if (status := result.status) != 200:
            raise OperationFailed(200, status)
        return ServerDatabase(result, self.id, self._client)
    
    async def delete(self) -> None:
        endpoint = f"/servers/{self.server_id}/databases/{self.id}"
        result = await self._client.api_request(endpoint, method="DELETE", json=False)
        if (status := result.status) != 204:
            raise OperationFailed(204, status)

class ServerDatabase(BasePteroObject, ServerDatabaseClient):
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