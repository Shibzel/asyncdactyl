from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass

from ....objects import BaseServer, BasePteroObject, Relationships
from ....exceptions import BadPowerState, OperationFailed
from ....constants import POWER_STATES

from .database import ClientServerDatabase, ClientServerDatabaseAPI


@dataclass
class WebsocketAuth:
    token: str
    socket: str

class Stats(BasePteroObject):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        
        data = data["attributes"]
        self.current_state: str = data["current_state"]
        self.is_suspended: bool = data["is_suspended"]
        self.resource_usage = ResouceUsage(**data["resources"])
    
@dataclass
class SftpDetails:
    ip: str
    port: int

@dataclass
class ResouceUsage:
    memory_bytes: int
    cpu_absolute: int
    disk_bytes: int
    network_rx_bytes: int
    network_tx_bytes: int

class ClientServerAPI:
    def __init__(self, client, uuid):
        self.client = client
        self.uuid = uuid

    async def fetch(self) -> "ClientServer":
        return await self.client._client.get_server(self.uuid)

    async def websocket(self) -> WebsocketAuth:
        endpoint = f"/client/servers/{self.uuid}/websocket"
        result = await self.client.api_request(endpoint)
        return WebsocketAuth(**result["data"])
    
    async def resource_usage(self) -> Stats:
        endpoint = f"/client/servers/{self.uuid}/resources"
        result = await self.client.api_request(endpoint)
        return Stats(result)
    
    async def send_command(self, command: str) -> None:
        endpoint = f"/client/servers/{self.uuid}/command"
        data = {"command": command}
        result = await self.client.api_request(endpoint, method="POST", data=data)
        if (status := result.status) != 204:
            raise OperationFailed(204, status)
        
    async def change_power_state(self, state: str) -> None:
        if not state in POWER_STATES:
            raise BadPowerState(state)

        endpoint = f"/client/servers/{self.uuid}/power"
        data = {"signal": state}
        result = await self.client.api_request(endpoint, method="POST", data=data)
        if (status := result.status) != 204:
            raise OperationFailed(204, status)
        
    async def list_databases(self, show_password: bool = False) -> List[ClientServerDatabase]:
        endpoint = f"/client/servers/{self.uuid}/databases"
        params = {"password": show_password}
        result = await self.client.api_request(endpoint, params=params)
        return [ClientServerDatabase(db, self.client) for db in result["data"]]
    
    async def get_database(
        self,
        database_id: str,
        fetch: bool = True
    ) -> Union[ClientServerDatabase, ClientServerDatabaseAPI]:
        if not fetch:
            return ClientServerDatabaseAPI(database_id, self.uuid, self.client)

        endpoint = f"/client/servers/{self.uuid}/databases/{database_id}"
        result = await self.client.api_request(endpoint)
        return ClientServerDatabase(result, self.uuid, self.client)
    
    async def create_database(self, name: str, remote: Optional[str] = "%") -> ClientServerDatabase:
        endpoint = f"/client/servers/{self.uuid}/databases"
        data = {"database": name, "remote": remote}
        result = await self.client.api_request(endpoint, method="POST", data=data)
        return ClientServerDatabase(result, self.uuid, self.client)

class ClientServer(BaseServer, ClientServerAPI):
    def __init__(self, data: Dict[str, Any], client):
        super().__init__(data)
        self.client = client

        data = data["data"]
        self.server_owner: bool = data["server_owner"]
        self.internal_id: int = data.get("internal_id")
        self.node: str = data["node"]
        self.is_node_under_maintenance: bool = data.get("is_node_under_maintenance")
        self.sftp_details = SftpDetails(**data["sftp_details"])
        self.invocation: str = data.get("invocation")
        self.is_suspended: bool = data["is_suspended"]
        self.is_installing: bool = data["is_installing"]
        self.relationships = Relationships(data["relationships"])
        
    @property
    def ip(self) -> str:
        if allocation := self.relationships.default_allocation:
            return allocation.ip
        
    @property
    def port(self) -> int:
        if allocation := self.relationships.default_allocation:
            return allocation.port