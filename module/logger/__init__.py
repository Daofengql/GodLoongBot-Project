from library.orm.extra import mysql_db_pool
from library.orm.table import Logger
from library.config import config
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.model import Group
from graia.ariadne.message.element import At,Image,Face,Source
import httpx
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    ArgumentMatch,
    ArgResult,
    WildcardMatch,
    ElementMatch,
    ElementResult,
    ParamMatch,
    RegexMatch
)
import datetime
from sqlalchemy import select,insert
import asyncio
import json


logger = Channel.current()
logger.name("消息记录插件")
logger.author("道锋潜鳞")
logger.description("记录机器人所有群聊聊天数据")

db = mysql_db_pool()


@logger.use(
    ListenerSchema(
        listening_events=[GroupMessage]
        )
    )
async def sign(
    app: Ariadne,
    message: MessageChain,
    event:GroupMessage,
    group: Group):
    image_urls = []
    if message.has(Image):
        for i in message.get(Image):
            image_urls.append(i.url)
    msgid = event.message_chain.get_first(Source).id
    msgtime = event.message_chain.get_first(Source).time
    dbsession = await db.get_db_session()
    
    try:
        async with dbsession() as session:
            await session.execute(
                insert(Logger).values(
                    qq = event.sender.id,
                    group=group.id,
                    msgid =msgid,
                    msg=message.display,
                    msgimage=str(image_urls),
                    sendtime = datetime.datetime.now()
                )
            )
            await session.commit()
    except:pass
