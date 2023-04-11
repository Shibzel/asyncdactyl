import asyncio
from functools import cached_property
from typing import Dict, Optional, Any, Union, Iterable
from urllib.parse import urlparse
try:
    from orjson import dumps
except ImportError:
    from json import dumps
import aiohttp

from . import __version__
from .exceptions import ClientConfigError, BadRequestType, RateLimitExceeded, BadRequestError, NotFound
from .api.client import ClientAPI
from .api.application import ApplicationAPI


class AsyncPterodactylClient:
    
    def __init__(
        self,
        url: str,
        api_key: str = None,
        override_headers: Dict[str, str] = None,
        extra_retry_codes: Iterable[int] = [],
        retries: int = 3,
        **aiohttp_kwargs
    ) -> None:
        self.retry_codes = [429, *extra_retry_codes]
        if retries < 0:
            raise ClientConfigError("The number of retries can't be sub 0.")
        self._retries = retries

        try:
            parsed_url = urlparse(url)
        except Exception as exc:
            raise ClientConfigError("Couldn't parse panel url.") from exc
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        self._base_url = base_url + "/api"
        
        if not api_key and not override_headers:
            url = base_url + "/account/api"
            raise ClientConfigError("No API key provided."
                f" You can get one at the following url : {base_url}")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"AsyncPydactyl/{__version__}"
        }
        self._session = aiohttp.ClientSession(self.base_url, json_serialize=dumps,
            headers=override_headers or headers, **aiohttp_kwargs)
        s = self._session
        self._session_methods = {"GET": s.get, "POST": s.post, "PATCH": s.patch,
                                 "DELETE": s.delete, "PUT": s.put}

    @property
    def base_url(self) -> str:
        return self._base_url

    async def api_request(
        self,
        endpoint,
        mode: Optional[str] = "GET",
        params: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        override_headers: Optional[Dict[str, str]] = None,
        json: bool = True
    ) -> Union[Dict[str, Any], aiohttp.ClientResponse]:
        s = self._session
        headers = s.headers
        if override_headers:
            headers = headers.copy()
            headers.update(override_headers)
        mode = mode.upper()
        if not (method := self._session_methods.get(mode)):
            raise BadRequestType(mode)

        for i in range(self._retries):
            response = await method(url=endpoint, data=data, params=params,
                                    headers=headers, json=json)
            if response.status not in self.retry_codes:
                break
            await asyncio.sleep(2**i)
            
        try:
            json_response: Dict = await response.json()
        except ValueError:
            json_response = {}
        
        if response.status == 429:
            raise RateLimitExceeded()
        elif response.status in (400, 422):
            raise BadRequestError(json_response.get("error"))
        elif response.status == 404:
            raise NotFound
        else:
            response.raise_for_status()
        
        return json_response if json else response

    @cached_property
    def client(self):
        return ClientAPI(self)

    @cached_property
    def application(self):
        return ApplicationAPI(self)