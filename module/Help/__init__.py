from graia.ariadne.event.mirai import NudgeEvent
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from library.config import config
from graia.ariadne.model import Group
import datetime
from graia.ariadne.message.element import Image, At, Plain, Source, AtAll
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    WildcardMatch,
    FullMatch
)


LAST_QEQUEST = datetime.datetime.now()

nudge = Channel.current()

async def limit_check():
    global LAST_QEQUEST
    nowtime = datetime.datetime.now()
    if (nowtime-LAST_QEQUEST) > datetime.timedelta(seconds = 20):
        LAST_QEQUEST = datetime.datetime.now()
        return True
    return False
    
    
@nudge.use(ListenerSchema(listening_events=[NudgeEvent]))
async def getup(app: Ariadne, event: NudgeEvent):
    if not event.target == config.account:
        return
    if not await limit_check():
        await app.send_message(
            event.group_id,
            MessageChain("别戳啦别戳啦，再戳要坏掉了~~")
        )
        return
    if event.context_type == "group":
        await app.send_group_message(
            event.group_id,
            MessageChain(f"{config.name}在，找{config.name}是有什么事吗？如需寻求帮助请查看使用文档{config.docs}")
        )
    elif event.context_type == "friend":
        await app.send_friend_message(
            event.friend_id,
            MessageChain(f"别戳{config.name}，{config.name}有点怕痒！")
        )
        

@nudge.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("帮助","菜单",".help").help("主控制器")
                ]
            )
        ],
        )
    )
async def getup(app: Ariadne, event: GroupMessage,group: Group):
    await app.send_group_message(
        target=group,
        message = MessageChain(f"{config.name}在，寻求帮助请查看使用文档{config.docs}")
    )
        

from library.vault import dbexec
d = dbexec()
@nudge.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("c1").help("主控制器")
                ]
            )
        ],
        )
    )
async def getup(app: Ariadne, event: GroupMessage,group: Group):
    print(2)
        