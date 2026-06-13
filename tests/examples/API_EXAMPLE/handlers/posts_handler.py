import configparser
from pathlib import Path
from typing import Optional

from playwright.async_api import APIRequestContext, APIResponse


class PostsHandler:
    def __init__(self, api_context: APIRequestContext):
        self.api_context = api_context
        self.host_name = "jsonplaceholder"
        self._config = configparser.ConfigParser()
        resources_path = Path(__file__).parent.parent.parent.parent / "api" / "resources" / "api_resources.ini"
        self._config.read(resources_path)

    def _build_url(self, endpoint_name: str, **kwargs) -> str:
        host = self._config.get("api_hosts", self.host_name)
        endpoint = self._config.get("api_endpoints", endpoint_name)
        for key, value in kwargs.items():
            endpoint = endpoint.replace(f"{{{key}}}", str(value))
        return f"{host}{endpoint}"

    async def get_all_posts(self) -> APIResponse:
        url = self._build_url("posts")
        return await self.api_context.get(url)

    async def get_post_by_id(self, post_id: int) -> APIResponse:
        url = self._build_url("post_by_id", id=post_id)
        return await self.api_context.get(url)

    async def create_post(self, data: dict) -> APIResponse:
        url = self._build_url("posts")
        return await self.api_context.post(url, data=data)
