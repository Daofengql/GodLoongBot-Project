from contextlib import contextmanager
from typing import Generator, Literal, TypedDict
from uuid import uuid4

from kayaku import create
from loguru import logger

from module.openai.api._base import OpenAIAPIBase
from module.openai.config import OpenAIConfig


class ChatEntry(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatNode(TypedDict):
    entry: ChatEntry
    id: str
    previous: str | None


class ChatResponseUsage(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponseChoice(TypedDict):
    message: ChatEntry
    finish_reason: Literal["stop", "length"]
    index: int


class ChatResponse(TypedDict):
    id: str
    object: str
    created: int
    model: str
    usage: ChatResponseUsage
    choices: list[ChatResponseChoice]


class ChatErrorDetail(TypedDict):
    message: str
    type: str
    param: str
    code: str


class ChatErrorResponse(TypedDict):
    error: ChatErrorDetail


class ChatCompletion(OpenAIAPIBase):
    OBJECT: str = "chat.completions"

    system: str
    """ System 角色 """

    nodes: list[ChatNode]
    """ 对话节点，包含所有对话记录 """

    history: list[ChatNode]
    """ 对话历史，不包含被删除的对话记录 """

    cache_size: int
    """ 缓存大小 """

    temperature: float
    """ ChatGPT Temperature """

    timeout: int

    _lock: bool = False
    """ 锁定状态 """

    def __init__(self, *, system: str = "", timeout: int = 30):
        self.system = system
        self.nodes = []
        self.history = []
        cfg: OpenAIConfig = OpenAIConfig()
        self.cache_size = cfg.chatgpt_cache
        self.temperature = cfg.chatgpt_temperature
        self.timeout = timeout

    @contextmanager
    def lock(self):
        assert not self._lock, "你先别急，还没说完"
        try:
            self._lock = True
            yield
        finally:
            self._lock = False

    @property
    def latest(self) -> ChatNode:
        return self.history[-1] if self.history else None

    def node_from_id(self, node_id: str) -> ChatNode | None:
        return next((node for node in self.nodes if node["id"] == node_id), None)

    async def call(
        self,
        node_id: str = None,
        cache_delta: int = 0,
        *,
        model: str = "gpt-3.5-turbo-16k",
        temperature: float = None,
        top_p: float = 1,
        n: int = 1,
        stream: bool = False,
        stop: str | list[str] = None,
        max_tokens: int = None,
        presence_penalty: float = 0,
        frequency_penalty: float = 0,
        logit_bias: dict = None,
        timeout: int = None,
        **kwargs,
    ):
        """
        调用 OpenAI ChatCompletion API

        Args:
            node_id (str, optional): 上一条对话记录的 UUID，为空则取最后一条. Defaults to None.
            cache_delta (int, optional): 缓存大小增量. Defaults to 0.
            model (str, optional): 模型. Defaults to "gpt-3.5-turbo".
            temperature (float, optional): ChatGPT Temperature. Defaults to None.
            top_p (float, optional): Top-p. Defaults to 1.
            n (int, optional): 生成数量. Defaults to 1.
            stream (bool, optional): 是否流式. Defaults to False.
            stop (str | list[str], optional): 停止词. Defaults to None.
            max_tokens (int, optional): 最大生成长度. Defaults to None.
            presence_penalty (float, optional): Presence Penalty. Defaults to 0.
            frequency_penalty (float, optional): Frequency Penalty. Defaults to 0.
            logit_bias (dict, optional): Logit Bias. Defaults to None.
            timeout (int, optional): 超时. Defaults to 30.

        Returns:
            ChatResponse: OpenAI ChatCompletion API 返回值

        Raises:
            AssertionError: 锁定状态
            TimeoutError: 超时
        """
        logit_bias = logit_bias or {}  # 防止 OpenAI 报类型错误
        with self.lock():
            cfg: OpenAIConfig = OpenAIConfig()
            if temperature is None:
                temperature = self.temperature
            if max_tokens is None:
                max_tokens = cfg.chatgpt_max_token
            if timeout is None:
                timeout = self.timeout
            return await self._call(
                timeout=timeout,
                model=model,
                messages=[ChatEntry(role="system", content=self.system)]
                + [node["entry"] for node in self.get_chain(node_id)][
                    -(self.cache_size + cache_delta) :  # noqa
                ],
                temperature=temperature,
                top_p=top_p,
                n=n,
                stream=stream,
                stop=stop,
                max_tokens=max_tokens,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
                logit_bias=logit_bias,
                **kwargs,
            )

    def add(self, entry: ChatEntry, node_id: str = None) -> str:
        """
        添加对话记录

        Args:
            entry (ChatEntry): 对话记录
            node_id (str, optional): 上一条对话记录的 UUID，为空则取最后一条. Defaults to None.

        Returns:
            str: 新对话记录的 UUID
        """
        if node_id is None and self.latest:
            node_id = self.latest["id"]
        node = ChatNode(entry=entry, id=str(uuid4()), previous=node_id)
        self.nodes.append(node)
        self.history.append(node)
        return node["id"]

    def get_chain(self, node_id: str) -> list[ChatNode]:
        """
        获取对话链

        Args:
            node_id (str): 节点 UUID

        Returns:
            list[ChatNode]: 对话链，由旧到新
        """
        return list(self.yield_previous(node_id))[::-1] + [self.node_from_id(node_id)]

    @staticmethod
    def _parse_response(resp: dict) -> ChatResponse | ChatErrorResponse:
        return ChatErrorResponse(**resp) if "error" in resp else ChatResponse(**resp)

    async def send(
        self,
        content: str,
        previous: str = None,
        *,
        role: Literal["system", "user", "assistant"] = "user",
        retries: int = 3,
        cache_delta: int = 0,
    ) -> tuple[tuple[str | None, str], tuple[str | None, str]]:
        """
        发送消息

        Args:
            content (str): 消息内容
            previous (str): 上一条消息
            role (Literal["system", "user", "assistant"], optional): 消息角色. Defaults to "user".
            retries (int, optional): 重试次数. Defaults to 3.
            cache_delta (int, optional): 缓存偏移量. Defaults to 0.

        Returns:
            tuple[tuple[str | None, str], tuple[str | None, str]]: 发送的消息和回复的消息
        """
        uuids: list[str] = []
        try:
            uuids.append((user := self.add(ChatEntry(role=role, content=content), previous)))
            data = self._parse_response(await self.call(user, cache_delta))
            if "error" not in data:
                data: ChatResponse
                uuids.append((reply := self.add(entry := (data["choices"][0]["message"]), node_id=user)))
                return (user, content), (reply, entry["content"])
            data: ChatErrorResponse
            match data["error"]["type"]:
                case "insufficient_quota":
                    raise ValueError("OpenAI API 配额不足，请联系管理员。")
                case "context_length_exceeded":
                    if retries > 0:
                        return await self.send(
                            content,
                            role=role,
                            retries=retries - 1,
                            cache_delta=cache_delta - 1,
                        )
                    raise ValueError("对话长度超过限制，请尝试缩减对话内容或清除会话记录。")
                case _:
                    raise ValueError("[非预期错误] " + data["error"]["message"])
        except AssertionError as e:
            return (None, content), (None, e.args[0])
        except TimeoutError:
            return (None, content), (None, "取得回复时发生错误：请求超时")
        except Exception as e:
            logger.exception(e)
            logger.error("[ChatSession] 取得回复时发生错误")
            self.remove(*uuids)
            return (None, content), (None, f"取得回复时发生错误：{e}")

    async def retry(self, node_id: str = None) -> str:
        """
        重试一条消息

        Args:
            node_id (str, optional): 消息 UUID，为空则重试最后一条. Defaults to None.

        Returns:
            str: 消息内容
        """
        if not node_id:
            node_id = self.latest["id"]
        try:
            data = self._parse_response(
                await self.call(self.get_previous(node_id)["id"])
            )
            if data.get("type") == "error":
                raise ValueError(data["message"])
            new = data["choices"][0]["message"]["content"]
            for node in self.history:
                if node["id"] == node_id:
                    node["entry"]["content"] = new
            return new
        except Exception as e:
            logger.exception(e)
            logger.error("[ChatSession] 取得回复时发生错误")
            return f"取得回复时发生错误：{e}"

    def pop(self, node_id: str) -> ChatNode:
        """
        弹出消息

        Args:
            node_id (str): 消息 UUID

        Raises:
            ValueError: 未找到消息
        """
        pop = None
        for i, node in enumerate(self.history):
            if node["id"] == node_id:
                pop = self.history.pop(i)
        if not pop:
            raise ValueError(f"未找到 UUID 为 {node_id} 的消息")
        for i, node in enumerate(self.history):
            if node["previous"] == node_id:
                self.history[i]["previous"] = pop["previous"]
        return pop

    def get_previous(self, node_id: str) -> ChatNode | None:
        """
        获取前置消息

        Args:
            node_id (str): 节点 UUID

        Returns:
            ChatNode: 前置消息
        """
        if not (this := self.node_from_id(node_id)):
            return
        for node in self.history:
            if node["id"] == this["previous"]:
                return node

    def yield_previous(self, node_id: str) -> Generator[ChatNode, None, None]:
        """
        获取前置消息

        Args:
            node_id (str): 节点 UUID

        Yields:
            Generator[ChatNode, None, None]: 前置消息
        """
        while node := self.get_previous(node_id):
            yield node
            node_id = node["id"]

    def revoke(self, count: int = 1, node_id: str = None):
        """
        撤回消息

        Args:
            count (int): 撤回条数
            node_id (str, optional): 撤回起始节点，为空则从最后一条开始撤回. Defaults to None.

        Raises:
            ValueError: 未找到消息
        """
        if not node_id:
            node_id = self.latest["id"]
        self.pop(node_id)
        for _ in range(count - 1):
            if not (node := self.get_previous(node_id)):
                break
            self.pop(node["id"])

    def remove(self, *uuids: str):
        """
        删除消息

        Args:
            *uuids (str): 消息 UUID

        Raises:
            ValueError: 未找到消息
        """
        for uuid in uuids:
            self.pop(uuid)

    def flush(self, system: bool = False):
        if system:
            self.system = ""
        self.history = []
        self.nodes = []
