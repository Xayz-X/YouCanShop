from __future__ import annotations
import logging
from typing import (
    Any,
    ClassVar,
    Union,
)
import json
from urllib.parse import quote as _uriquote
from urllib.parse import quote_plus
import aiohttp

from .errors import StoreException, ValidationError, ClosedStore, NotFound, ServerError

_log = logging.getLogger(__name__)


def _to_json(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)


async def json_or_text(response: aiohttp.ClientResponse) -> Union[dict[str, Any], str]:
    try:
        text = await response.text(encoding="utf-8")
        if response.headers.get("content-type", "").startswith("application/json"):
            return json.loads(text)
    except KeyError:
        pass
    return text


class Route:
    BASE: ClassVar[str] = "https://api.youcan.shop"

    def __init__(
        self,
        method: str,
        path: str,
        *,
        metadata: str | None = None,
        **parameters: Any,
    ) -> None:
        self.path: str = path
        self.method: str = method
        self.metadata: str | None = metadata
        url = self.BASE + self.path
        if parameters:
            url = url.format_map(
                {
                    k: _uriquote(v) if isinstance(v, str) else v
                    for k, v in parameters.items()
                }
            )
        self.url: str = url


class HTTPClient:
    def __init__(
        self,
        connector: aiohttp.BaseConnector | None = None,
    ) -> None:
        self.connector: aiohttp.BaseConnector = connector or aiohttp.TCPConnector()
        self.__session: aiohttp.ClientSession | None = None
        self.token: str | None = None

    async def start_session(self) -> None:
        if not self.__session:
            self.__session = aiohttp.ClientSession(connector=self.connector)

    def clear(self) -> None:
        if self.__session and not self.__session.closed:
            self.__session = None

    async def close(self) -> None:
        if self.__session:
            await self.__session.close()
            self.__session = None

    async def request(
        self,
        route: Route,
        **kwargs: Any,
    ) -> Any:

        method = route.method
        url = route.url

        headers: dict[str, str] = {}

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        if "json" in kwargs:
            headers["Content-Type"] = "application/json"
            kwargs["json"] = _to_json(kwargs.pop("json"))

        kwargs["headers"] = headers

        try:
            async with self.__session.request(method, url, **kwargs) as response:

                _log.debug(
                    f"{method} {url} with {kwargs.get('json')} has returned {response.status}"
                )

                data = await json_or_text(response)  # try to parse the data

                if response.status >= 400:
                    error_data = (
                        await response.json()
                        if response.headers.get("content-type", "").startswith(
                            "application/json"
                        )
                        else {}
                    )

                    if response.status == 402:
                        raise ClosedStore(
                            status=response.status,
                            error="Store Closed",
                            details=error_data.get("error", "No details provided"),
                        )
                    elif response.status == 404:
                        raise NotFound(
                            status=response.status,
                            error="Not Found",
                            details=error_data.get("detail", "No details provided"),
                        )
                    elif response.status == 422:
                        raise ValidationError(
                            status=response.status,
                            error="Validation Error",
                            details=error_data.get("detail", "No details provided"),
                        )
                    else:
                        raise StoreException(
                            status=response.status,
                            error=error_data.get("error", "Unknown error"),
                            details=error_data.get("detail", "No details provided"),
                        )
                return data

        except aiohttp.ClientError as e:
            _log.error(f"Request failed: {e}")
            raise ServerError(
                status=500,
                error="Request Failed",
                details="Failed to establish a connection to server.",
            )

    def _login(self, email: str, password: str) -> Any:
        payload = {"email": email, "password": password}
        return self.request(Route("POST", "/auth/login"), data=payload)

    def _stores(self) -> Any:
        return self.request(Route("GET", "/stores"))

    def _get_products(self) -> Any:
        return self.request(Route("GET", "/products"))

    def _search_orders(self, search_value) -> Any:
        return self.request(Route("GET", f"/orders?q={quote_plus(search_value)}"))

    def _order_fulfill(
        self, order_id: str, seller_note: str, tracking_number: str
    ) -> Any:
        payload = {"seller_note": seller_note, "tracking_number": tracking_number}
        return self.request(Route("PUT", f"/orders/{order_id}/fulfill"), json=payload)
