import contextlib
import time
from abc import ABC
from asyncio import Lock

from creart import (AbstractCreator, CreateTargetInfo, add_creator,
                    exists_module)
from graia.ariadne import Ariadne
from graia.ariadne.message.element import Source
from graia.ariadne.model import Group
from loguru import logger

from library import config


class PublicGroup:
    """公共群分发"""

    accounts: set[int]
    """ 已登录账号 """

    data: dict[int, set[int]]
    """ 群组数据 """

    _lock: Lock

    def __init__(self):
        self.accounts = set()
        self.data = {}
        self._lock = Lock()

    async def init_account(self, account: int):
        async with self._lock:
            with contextlib.suppress(Exception):
                app = Ariadne.current(account)
                for group in await app.get_group_list():
                    group = int(group)
                    if group in self.data:
                        self.data[group].add(app.account)
                    else:
                        self.data[group] = {app.account}
            self.accounts.add(app.account)
            logger.success(f"[PublicGroup] {account}: 公共群数据初始化完成")

    async def init_all(self):
        """初始化数据"""
        await self.init_account(config.account)

    def add_group(self, group: Group | int, account: int):
        """
        添加群组

        Args:
            group (Group | int): 群组
            account (int): 账号
        """
        group = int(group)
        if group in self.data:
            self.data[group].add(account)
        else:
            self.data[group] = {account}

    def remove_group(self, group: Group | int, account: int):
        """
        移除群组

        Args:
            group (Group | int): 群组
            account (int): 账号
        """
        group = int(group)
        if group in self.data and self.data[group]:
            self.data[group].remove(account)

    def get_index(self, group: Group | int, account: int) -> int:
        """
        获取索引

        Args:
            group (Group | int): 群组
            account (int): 账号

        Returns:
            int: 索引

        Raises:
            ValueError: 未找到索引
        """
        group = int(group)
        if group in self.data and account in self.data[group]:
            return sorted(list(self.data[group])).index(account)
        raise ValueError

    def get_accounts(self, group: Group | int) -> set[int]:
        """
        获取账号列表

        Args:
            group (Group | int): 群组

        Returns:
            set[int]: 账号列表
        """
        group = int(group)
        return self.data[group] if group in self.data else set()

    async def remove_account(self, account: int):
        """
        移除账号

        Args:
            account (int): 账号
        """
        async with self._lock:
            for group in self.data:
                if account in self.data[group]:
                    self.data[group].remove(account)
            self.accounts.remove(account)
            logger.success(f"[PublicGroup] {account}: 公共群数据移除完成")

    def need_distribute(self, group: Group | int, account: int) -> bool:
        """
        是否需要分发

        Args:
            group (Group | int): 群组
            account (int): 账号

        Returns:
            bool: 是否需要分发
        """
        group = int(group)
        if group in self.data and account in self.data[group]:
            return len(self.data[group]) > 1
        return False

    def execution_stop(self, group: Group | int, account: int, source: Source) -> bool:
        """
        是否执行停止

        Args:
            group (Group | int): 群组
            account (int): 账号
            source (Source): 消息链 Source

        Returns:
            bool: 是否执行停止
        """
        group = int(group)
        if group not in self.data:
            self.add_group(group, account)
            return True
        if account not in self.data[group]:
            self.add_group(group, account)
            return True
        return (source.id + int(time.mktime(source.time.timetuple()))) % len(
            self.data[group]
        ) != self.get_index(group, account)


class PublicGroupClassCreator(AbstractCreator, ABC):
    targets = (
        CreateTargetInfo("library.util.multi_account.public_group", "PublicGroup"),
    )

    @staticmethod
    def available() -> bool:
        return exists_module("library.util.multi_account.public_group")

    @staticmethod
    def create(_create_type: type[PublicGroup]) -> PublicGroup:
        return PublicGroup()


add_creator(PublicGroupClassCreator)