import json
from typing import Any, Optional

from playwright.async_api import APIRequestContext, APIResponse


class ApiHandler:
    def __init__(self, api_context: APIRequestContext):
        self.api_context = api_context

    async def get(
        self,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> APIResponse:
        return await self.api_context.get(url, headers=headers, params=params)

    async def post(
        self,
        url: str,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> APIResponse:
        return await self.api_context.post(url, data=data, headers=headers)

    async def put(
        self,
        url: str,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> APIResponse:
        return await self.api_context.put(url, data=data, headers=headers)

    async def delete(
        self, url: str, headers: Optional[dict] = None
    ) -> APIResponse:
        return await self.api_context.delete(url, headers=headers)

    async def patch(
        self,
        url: str,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> APIResponse:
        return await self.api_context.patch(url, data=data, headers=headers)

    @staticmethod
    def build_curl(
        method: str, url: str, headers: Optional[dict] = None, data: Optional[dict] = None
    ) -> str:
        parts = [f"curl -X {method.upper()} '{url}'"]

        if headers:
            for key, value in headers.items():
                parts.append(f"  -H '{key}: {value}'")

        if data:
            parts.append(f"  -d '{json.dumps(data)}'")

        return " \\\n".join(parts)
