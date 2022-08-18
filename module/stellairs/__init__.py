from library.config import config
from graia.ariadne.app import Ariadne
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    WildcardMatch,
)
from library.Bot import bot
from graia.saya import Channel
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast import ListenerSchema
from graia.broadcast.interrupt import Waiter, InterruptControl
from library.image.oneui_mock.elements import *
from graia.ariadne.message.element import Image, At, Plain, Source
from graia.ariadne.model import Group
import os
from library.orm.extra import mysql_db_pool
from .utils import (
    DailySignin,
    getGroupRank,
    getMyInfo,
    worShip
)
import aiofiles

stellairs = Channel.current()

stellairs.name("模拟群星")
stellairs.author("道锋潜鳞")
stellairs.description("模拟stellaris，舰队挑战")

db = mysql_db_pool()
PATH = os.path.dirname(__file__) + "/assets/"


"""临时屏蔽测试，提交记得删除
@stellairs.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("签到").help("主控制器") @ "func",
                    WildcardMatch() @ "param",
                ]
            )
        ],
    )
)

"""
@stellairs.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(".Galaxy", "逐鹿星河").help("主控制器"),
                    UnionMatch(
                        "-Signin","获取今日能量币","签到",
                        "-MyInfo","我的信息",
                        "-LocalRank","本星海排名",
                        "-Worhip","崇拜",
                        "~","控制台",
                    )
                    @ "func",
                    WildcardMatch() @ "param",
                ]
            )
        ],
    )
)
async def stellairs_handle(
    app: Ariadne,
    group: Group,
    event: GroupMessage,
    message: MessageChain,
    param: MatchResult,
    func: MatchResult,
):
    param = param.result.display
    func = func.result.display

    aioHTTPsession = Ariadne.service.client_session

    if func in ("-Signin", "获取今日能量币", "签到"):
        ret = await DailySignin(app, group, event)
    elif func in ("-MyInfo", "我的信息"):
        ret = await getMyInfo(app, group, event)
    elif func in ("-Worhip","崇拜"):
        ret = await worShip(app, group, event,message)
    elif func in ("-LocalRank", "本星海排名") and param in (
        "",
        "综合排名",
        "能量币排行",
        "合金排行",
        "凝聚力排行",
    ):
        ret = await getGroupRank(app, group, event, param)
    elif func in ("~", "控制台"):
        async with aiofiles.open(PATH + "another/~.gif", "rb") as f:
            ret = MessageChain(
                Image(data_bytes=await f.read()), Plain(f"想啥呢，这是多人联机，哪来的💀第四天灾（")
            )
    else:
        ret = MessageChain(f"啊哦，顾问{config.name}不知道您想干嘛")

    await app.send_group_message(group, ret)
