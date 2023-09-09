from datetime import datetime, timedelta

from graia.ariadne import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage
from graia.ariadne.message.chain import MessageChain, Quote
from graia.ariadne.message.element import Forward, ForwardNode,Image,Plain

import aiohttp

from module.openai.api.chat import ChatCompletion

from library.md2img import M2I

from .message import send_message


m2i = M2I()

Message = GroupMessage | FriendMessage
"""监听的消息类型"""


class ChatSession:
    instance: ChatCompletion
    mapping: dict[int, str]

    def __init__(self):
        self.instance = ChatCompletion()
        self.mapping = {}

    async def remove(self, app: Ariadne, event: Message, quote: Quote):
        if quote.id in self.mapping:
            self.instance.remove(self.mapping[quote.id])
            del self.mapping[quote.id]
            return await send_message(event, MessageChain("已删除该条目"), app.account)
        return await send_message(event, MessageChain("未找到该条目"), app.account)

    async def revoke(self, app: Ariadne, event: Message, quote: Quote, count: int):
        if quote.id in self.mapping:
            self.instance.revoke(count, self.mapping[quote.id])
            return await send_message(event, MessageChain("已撤回该条目"), app.account)
        return await send_message(event, MessageChain("未找到该条目"), app.account)

    async def send(
        self, app: Ariadne, event: Message, content: str, quote: Quote | None = None
    ):
        (user_id, _), (reply_id, reply_content) = await self.instance.send(
            content, self.mapping.get(quote.id) if quote else quote
        )


        if len(reply_content) >200 or "`" in reply_content:
            async with aiohttp.ClientSession() as session:
                repreply_img = await m2i.GetChromeTextFromRemoteServer(content=reply_content,session=session)
                uid = await m2i.genWEBuid(reply_content)

                mess =  [Image(data_bytes=repreply_img),Plain("\n在线查看(链接1小时有效)："),Plain(f"https://web-bot.loongapi.com/md2img/{uid}")]
        else:
            mess = [Plain(reply_content)]

        active = await send_message(event, MessageChain(*mess), app.account)
        if user_id and reply_id:
            self.mapping[event.id] = user_id
            self.mapping[active.id] = reply_id

    async def get_chain(self, app: Ariadne, event: Message, quote: Quote):
        if chain := self.instance.get_chain(self.mapping.get(quote.id)):
            return await send_message(
                event,
                MessageChain(
                    Forward(
                        [
                            ForwardNode(
                                target=8000_0000
                                if node["entry"]["role"] == "user"
                                else app.account,
                                time=datetime.now()
                                - timedelta(minutes=len(chain))
                                + timedelta(minutes=index),
                                message=MessageChain(node["entry"]["content"]),
                                name="用户"
                                if node["entry"]["role"] == "user"
                                else "ChatGPT",
                            )
                            for index, node in enumerate(chain)
                        ]
                    )
                ),
                app.account,
            )
        return await send_message(event, MessageChain("未找到该条目"), app.account)

    async def flush(self, app: Ariadne, event: Message, system: bool):
        self.instance.flush(system)
        return await send_message(event, MessageChain("已清空"), app.account)

    async def set_system(self, app: Ariadne, event: Message, system: str):
        self.instance.system = system
        return await send_message(event, MessageChain("已设置 system prompt"), app.account)


class ChatSessionContainer:
    session: dict[int, ChatSession] = {}

    @classmethod
    def get_or_create(cls, field: int) -> ChatSession:
        if field not in cls.session:
            cls.session[field] = ChatSession()
        return cls.session[field]
