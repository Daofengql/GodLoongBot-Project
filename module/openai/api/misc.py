import json
import random
import re
from contextlib import contextmanager, suppress
from typing import Generator, Iterable, Literal, TypeVar

import graia.ariadne.message.element
from aiohttp import ClientResponseError, ClientSession
from creart import it
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import MultimediaElement
from graia.ariadne.model import Group
from abc import ABC

from creart import AbstractCreator, CreateTargetInfo, exists_module
from loguru import logger
from creart import add_creator


Field = Group | Literal[0]
"""聊天区域"""

FieldWide = Field | int
"""聊天区域宽泛类型"""


class SessionContainer:
    """会话容器"""

    _session: dict[str, ClientSession] = {}

    async def get(
        self,
        name: str = "universal",
        flush: bool = False,
        base_url: str = None,
        /,
        **kwargs,
    ) -> ClientSession:
        """
        获取一个 aiohttp.ClientSession 对象

        Args:
            name: 会话名称
            flush: 是否刷新会话
            base_url: 会话的基础 URL，仅会在创建时生效
            **kwargs: 传递给 aiohttp.ClientSession 的参数

        Returns:
            aiohttp.ClientSession 对象
        """
        if flush or name not in self._session or self._session[name].closed:
            self._session[name] = ClientSession(base_url=base_url, **kwargs)
            logger.success(f"[SessionContainer] Created session {name!r}")
        return self._session[name]

    async def close(self, name: str):
        """
        关闭一个 aiohttp.ClientSession 对象

        Args:
            name: 会话名称
        """
        if name in self._session.copy():
            await self._session[name].close()
            del self._session[name]
            logger.success(f"[SessionContainer] Closed session {name!r}")

    async def close_all(self):
        """关闭所有 aiohttp.ClientSession 对象，不应被手动调用"""
        for name in self._session.copy():
            with suppress(Exception):
                await self.close(name)




class SessionContainerCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("module.openai.api.misc", "SessionContainer"),)

    @staticmethod
    def available() -> bool:
        return exists_module("module.openai.api.misc")

    @staticmethod
    def create(_create_type: type[SessionContainer]) -> SessionContainer:

        return SessionContainer()
add_creator(SessionContainerCreator)

_T = TypeVar("_T")

IMAGE_URL = "https://gchat.qpic.cn/gchatpic_new/0/0-0-{id}/0"


def seconds_to_string(
    time: int | float,
    *,
    repr_ms: bool = True,
    ms_accuracy: int = 2,
    zh_cn: bool = True,
) -> str:
    """
    将秒数转换为字符串

    Args:
        time: 秒数
        repr_ms: 是否显示毫秒
        ms_accuracy: 毫秒精度
        zh_cn: 是否使用中文

    Returns:
        转换后的字符串
    """
    seconds, ms = divmod(time, 1)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    months, weeks = divmod(weeks, 4)
    years, months = divmod(months, 12)
    seconds = int(seconds)
    interval_repr = f"{seconds:02d}{' 秒' if zh_cn else 's'}"
    if ms and repr_ms:
        interval_repr += (
            f" {str(int(ms * 1000))[:ms_accuracy]}{' 毫秒' if zh_cn else 'ms'}"
        )
    if minutes := int(minutes):
        interval_repr = f"{minutes:02d}{' 分' if zh_cn else 'm'} {interval_repr}"
    if hours := int(hours):
        interval_repr = f"{hours:02d}{' 时' if zh_cn else 'h'} {interval_repr}"
    if days := int(days):
        interval_repr = f"{days}{' 天' if zh_cn else 'd'} {interval_repr}"
    if weeks := int(weeks):
        interval_repr = f"{weeks}{' 周' if zh_cn else 'w'} {interval_repr}"
    if months := int(months):
        interval_repr = f"{months}{' 月' if zh_cn else 'M'} {interval_repr}"
    if years := int(years):
        interval_repr = f"{years}{' 年' if zh_cn else 'y'} {interval_repr}"
    return interval_repr


def inflate(*obj: Iterable[_T]) -> list[_T]:
    """
    将多个可迭代对象合并为一个列表

    Args:
        obj: 可迭代对象

    Returns:
        合并后的列表
    """
    result = []
    for o in obj:
        if isinstance(o, Generator):
            o = list(o)
        if isinstance(o, (tuple, list, set)):
            result.extend(inflate(*o))
        else:
            result.append(o)
    return result


QUOTE_PATTERN = re.compile(r"""(".+?"|'.+?'|[^ "']+)""")


def camel_to_snake(name: str) -> str:
    """
    将驼峰命名法转换为下划线命名法

    Args:
        name: 驼峰命名法字符串

    Returns:
        下划线命名法字符串
    """
    return "_".join(re.sub(r"([A-Z])", r"_\1", name).lower().split("_")).strip("_")


def extract_field(event: MessageEvent) -> FieldWide:
    return event.sender.group if isinstance(event, GroupMessage) else 0


async def get_bytes(element: MultimediaElement) -> bytes:
    assert element.url or element.base64, "url or base64 is required"
    if element.base64:
        logger.success(f"[get_bytes] Element(id={element.id}): loaded from base64")
        return bytes.fromhex(element.base64)
    session = await it(SessionContainer).get()
    try:
        async with session.get(element.url) as resp:
            resp.raise_for_status()
            logger.success(f"[get_bytes] Element(id={element.id}): loaded from url")
            return await resp.read()
    except ClientResponseError as e:
        logger.warning(
            f"[get_bytes] Element(id={element.id}): "
            f"fallback to cache url due to {e}"
        )
        img_id = re.search(r"{(.+?)}", element.id)[1].replace("-", "")
        async with session.get(IMAGE_URL.format(id=img_id)) as resp:
            resp.raise_for_status()
            logger.success(
                f"[get_bytes] Element(id={element.id}): loaded from cache url"
            )
            return await resp.read()


def rebuild_chain(data: list[dict] | str) -> MessageChain:
    if isinstance(data, str):
        data = json.loads(data)
    elements = []
    for i in data:
        try:
            if not isinstance(i, dict):
                continue
            if not (typ := i.get("type", None)):
                continue
            if ele := graia.ariadne.message.element.__dict__.get(typ, None):
                elements.append(ele(**i))
        except NameError:
            logger.warning(f"[rebuild_chain] Unsupported element: {i['type']}")
    return MessageChain(elements)


@contextmanager
def seed_random(
    seed: int | float | str | bytes | bytearray | None = None, version: int = 2
):
    """
    随机种子上下文管理器

    Args:
        seed: 随机种子
        version: 随机种子版本

    Returns:
        None
    """
    try:
        random.seed(seed, version=version)
        yield
    finally:
        random.seed()


def weighed_random(
    data: list[_T],
    weights: list[int | float],
    count: int = 1,
    *,
    seed: int | None = None,
) -> list[_T]:
    """
    加权不重复随机

    Args:
        data: 数据列表
        weights: 权重列表
        count: 随机数量
        seed: 随机种子

    Returns:
        随机结果
    """
    assert len(data) == len(weights), (
        f"data and weights must be the same length, "
        f"got {len(data)} and {len(weights)}"
    )
    assert count <= len(data), (
        f"count must be less than or equal to the length of data, "
        f"got {count} and {len(data)}"
    )
    with seed_random(seed):
        result = []
        while len(result) < count:
            index = random.choices(range(len(data)), weights=weights)[0]
            result.append(data[index])
            data.pop(index)
            weights.pop(index)
    return result
