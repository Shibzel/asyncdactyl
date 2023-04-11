from typing import Dict, Any, Union, List, Optional
from dataclasses import dataclass
from datetime import datetime

from ...objects import BaseUser, BasePteroObject
from ...exceptions import OperationFailed


@dataclass
class ToptQRCodeImage:
    image_url_data: str
    secret: Union[str, None] = None

class ApiKey(BasePteroObject):
    def __init__(self, _data: Dict[str, Any]):
        super().__init__(_data)

        data = _data["attributes"]
        self.identifier: str = data["identifier"]
        self.description: str = data["description"]
        self.allowed_ips: List[str] = data["allowed_ips"]
        last_used = data["last_used_at"]
        self.last_used_at: datetime = self.strptime(last_used) if last_used else None
        self.created_at: datetime = self.strptime(data["created_at"])
        if meta := _data["meta"]:
            self.secret_token = meta["secret_token"]
        else:
            self.secret_token = None

class AccountAPI:
    def __init__(self, client):
        self.client = client

    async def fetch(self) -> "Account":
        return await self.client._client.get_account()

    async def get_2fa_details(self) -> ToptQRCodeImage:
        endpoint = "/client/account/two-factor"
        result = await self.client.api_request(endpoint)
        return ToptQRCodeImage(**result["data"])

    async def enable_2fa(self, code: Union[str, int]) -> List[str]:
        endpoint = "/client/account/two-factor"
        data = {"code": str(code)}
        result = await self.client.api_request(endpoint, "POST", data=data)
        return result
    
    async def disable_2fa(self, password: str) -> None:
        endpoint = "/client/account/two-factor"
        data = {"password": password}
        result = await self.client.api_request(endpoint, "DELETE", data=data, json=False)
        if (status := result.status) != 204:
            raise OperationFailed(204, status)
    
    async def update_email(self, email: str, password: str) -> None:
        endpoint = "/client/account/email"
        data = {"email": email, "password": password}
        result = await self.client.api_request(endpoint, "PUT", data=data, json=False)
        if (status := result.status) != 201:
            raise OperationFailed(201, status)

    async def update_password(
        self, 
        current_password: str, 
        password: str, 
        password_confirmation: Optional[str] = None
    ) -> None:
        endpoint = "/client/account/password"
        data = {
            "current_password": current_password,
            "password": password,
            "password_confirmation": password_confirmation or password  # Not really safe lmao
        }
        result = await self.client.api_request(endpoint, "PUT", data=data, json=False)
        if (status := result.status) != 204:
            raise OperationFailed(204, status)

    async def list_api_keys(self) -> List[ApiKey]:
        endpoint = "/client/account/api-keys"
        result = await self.client.api_request(endpoint)
        return [ApiKey(key) for key in result["data"]]

    async def create_api_key(self, description: str, allowed_ips: Optional[List[str]] = None):
        endpoint = "/client/account/api-keys"
        data = {"description": description}
        if allowed_ips:
            data["allowed_ips"] = allowed_ips
        result = await self.client.api_request(endpoint, "POST", data=data, json=False)
        if (status := result.status) != 201:
            raise OperationFailed(201, status)

    async def delete_api_key(self, api_key_id: str):
        endpoint = f"/client/account/api-keys/{api_key_id}"
        result = await self.client.api_request(endpoint, "DELETE", json=False)
        if (status := result.status) != 204:
            raise OperationFailed(204, status)

class Account(BaseUser, AccountAPI):
    def __init__(self, data: Dict[str, Any], client):
        super().__init__(data)
        self.client = client

        data = data["attributes"]
        self.admin = data["admin"]