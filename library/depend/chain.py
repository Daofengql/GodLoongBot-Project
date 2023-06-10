from abc import abstractmethod
from typing import TypeVar

from graia.ariadne.event import MiraiEvent
from graia.ariadne.message import Quote
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At
from graia.broadcast import (Decorator, DecoratorInterface, ExecutionStop,
                             RequirementCrashed)

from library.config import config

_T = TypeVar("_T")
_TD = TypeVar("_TD")


class EricDecorator(Decorator):
    @property
    @abstractmethod
    def supported_events(self) -> set[type[MiraiEvent]]:
        """装饰器支持的事件类型，空集合表示支持所有事件"""
        return set()

    @staticmethod
    async def lookup_param(
        interface: DecoratorInterface, name: str, annotation: type[_T], default: _TD
    ) -> _T | _TD:
        try:
            return await interface.dispatcher_interface.lookup_param(
                name, annotation, default
            )
        except RequirementCrashed:
            return default

    @abstractmethod
    async def target(self, interface: DecoratorInterface):
        pass

class QuotingOrAtMe(EricDecorator):
    pre = True
    one_at: bool

    @property
    def supported_events(self) -> set[type[MiraiEvent]]:
        return set()

    def __init__(self, one_at: bool = False):
        self.one_at = one_at

    async def _check_quote(self, i: DecoratorInterface) -> bool:
        quote: Quote | None = await self.lookup_param(
            i, "__decorator_parameter_quote__", Quote | None, None
        )
        if not quote:
            return False

    async def _check_at(self, i: DecoratorInterface) -> bool:
        chain = await self.lookup_param(
            i, "__decorator_parameter__", MessageChain, None
        )
        if not (ats := chain.get(At)):
            return False
        return (
            len(set([config.account]).intersection(at.target for at in ats)) == 1
            if self.one_at
            else any(at.target in [config.account] for at in ats)
        )

    async def target(self, i: DecoratorInterface):
        try:
            if not (await self._check_quote(i) or await self._check_at(i)):
                raise RequirementCrashed
        except RequirementCrashed as e:
            raise ExecutionStop from e
        return await i.dispatcher_interface.lookup_param(
            "__decorator_parameter__", MessageChain, None
        )