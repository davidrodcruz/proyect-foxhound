import configparser
from pathlib import Path
from typing import Any, Optional

from playwright.async_api import APIRequestContext, APIResponse


class HttpHandler:
    def __init__(self, api_context: APIRequestContext):
        self.api_context = api_context
        self._config = configparser.ConfigParser()
        resources_path = Path(__file__).parent.parent / "resources" / "api_resources.ini"
        self._config.read(resources_path)

    def get_host_url(self, host_name: str) -> str:
        return self._config.get("api_hosts", host_name)

    def get_endpoint(self, endpoint_name: str) -> str:
        return self._config.get("api_endpoints", endpoint_name)

    def build_url(self, host_name: str, endpoint_name: str, **kwargs) -> str:
        host = self.get_host_url(host_name)
        endpoint = self.get_endpoint(endpoint_name)

        for key, value in kwargs.items():
            endpoint = endpoint.replace(f"{{{key}}}", str(value))

        return f"{host}{endpoint}"

    async def send_request(
        self,
        method: str,
        host_name: str,
        endpoint_name: str,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
        **kwargs,
    ) -> APIResponse:
        url = self.build_url(host_name, endpoint_name, **kwargs)

        method = method.upper()
        if method == "GET":
            return await self.api_context.get(url, headers=headers)
        elif method == "POST":
            return await self.api_context.post(url, data=data, headers=headers)
        elif method == "PUT":
            return await self.api_context.put(url, data=data, headers=headers)
        elif method == "DELETE":
            return await self.api_context.delete(url, headers=headers)
        elif method == "PATCH":
            return await self.api_context.patch(url, data=data, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    @staticmethod
    def build_curl(
        method: str, url: str, headers: Optional[dict] = None, data: Optional[dict] = None
    ) -> str:
        import json

        parts = [f"curl -X {method.upper()} '{url}'"]

        if headers:
            for key, value in headers.items():
                parts.append(f"  -H '{key}: {value}'")

        if data:
            parts.append(f"  -d '{json.dumps(data)}'")

        return " \\\n".join(parts)
