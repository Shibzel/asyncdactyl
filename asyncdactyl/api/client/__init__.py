from typing import List, Union

from .permissions import Permissions
from .server import ClientServer, ClientServerAPI
from .account import Account, AccountAPI


class ClientAPI:
    def __init__(self, client):
        self.client = client

        self._account = None
        self._servers = {}

    async def show_permissions(self):
        endpoint = f"/client/permissions"
        result = await self.client.api_request(endpoint)
        return Permissions(result)

    async def list_servers(self) -> List[ClientServer]:
        endpoint = "/client"
        result = await self.api_request(endpoint)
        return [ClientServer(data) for data in result["data"]]
    
    async def get_server(self, server_id: str, fetch: bool = True) -> Union[ClientServer, ClientServerAPI]:
        if not fetch:
            if not (server := self._servers.get(server_id)):
                server = ClientServerAPI(self.client, server_id)
                self._servers[server_id] = server
            return server

        endpoint = f"/client/servers/{server_id}"
        result = await self.client.api_request(endpoint)
        return ClientServer(result)

    async def get_account(self, fetch: bool = True) -> Union[Account, AccountAPI]:
        if not fetch:
            if not self._account:
                self._account = AccountAPI(self.client)
            return self._account
        
        endpoint = f"/client/servers/account"
        result = await self.client.api_request(endpoint)
        return Account(result)
