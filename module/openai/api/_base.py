import asyncio
import random

from creart import it
from graia.saya import Channel

from module.openai.config import OpenAIConfig

from .misc import SessionContainer

channel = Channel.current()


class OpenAIAPIBase:
    BASE: str = "https://api.openai.com/v1"
    OBJECT: str

    @property
    def headers(self) -> dict[str, str]:
        cfg: OpenAIConfig = OpenAIConfig()
        if not cfg.api_keys:
            raise ValueError("OpenAI API Key 未配置")
        api_key: str = random.choice(cfg.api_keys)
        return {"ContentType": "application/json", "Authorization": f"Bearer {api_key}"}

    @property
    def url(self) -> str:
        return f"{self.BASE}/" + self.OBJECT.replace(".", "/")

    async def _call_impl(self, /, **kwargs) -> dict:
        session = await it(SessionContainer).get(channel.module)
        async with session.post(
                self.url, headers=self.headers, json=kwargs
        ) as resp:
            return await resp.json()

    async def _call(self, /, timeout: int = 30, **kwargs) -> dict:
        return await asyncio.wait_for(self._call_impl(**kwargs), timeout=timeout)
