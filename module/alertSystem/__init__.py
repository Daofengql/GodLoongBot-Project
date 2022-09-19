import asyncio
import aiohttp
from collections import deque
from library.config import config

from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Image, At, Plain, Source, AtAll
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast import ListenerSchema
from graia.ariadne.model import Group
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from graia.saya import Channel
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    WildcardMatch,
)

from .data import get_sub_group, parse_eq_data, change_sub_status

aleater = Channel.current()


INIT_LIST = deque(maxlen=150)

async def init():
    global INIT_LIST
    async with aiohttp.ClientSession() as session:
            
        async with session.get("http://www.ceic.ac.cn/daochu/id:1") as response:
            x1 = await response.text()

        INIT_LIST = await parse_eq_data(x1)



loop = asyncio.get_event_loop()
loop.run_until_complete(init())

@aleater.use(SchedulerSchema(timers.every_custom_seconds(50)))
async def every_minute_speaking(app: Ariadne):
    global INIT_LIST

    session = Ariadne.service.client_session

    subgroup = await get_sub_group("eq")
    
    async with session.get("http://www.ceic.ac.cn/daochu/id:1") as response:
        x2 = await response.text()

    x2 = await parse_eq_data(x2)

    for i in x2:
        if i not in INIT_LIST:
            INIT_LIST.append(i)
            message = f"根据中国地震台网速报：{i['time']} 在 {i['addr']} （{i['longitude']}° {i['latitude']}°）发生里氏 {i['level']}级地震，震源深度{i['depth']}KM \n本数据来源中国地震台网，http://www.ceic.ac.cn，正式数据以官方通知为准"
            
            for group in subgroup:
                await app.send_group_message(
                    target=group,
                    message=message
                )


@aleater.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("消息订阅管理", ".sub").help("主控制器"),
                    UnionMatch(
                        "-EarthQuack","地震通知"
                    ) @ "func",
                    UnionMatch(
                        "开启","enable",
                        "关闭","disable",
                        "状态","status",
                    ) @ "do"
                ]
            )
        ],
    )
)
async def sub_system_controller(
    app: Ariadne,
    group: Group,
    event: GroupMessage,
    do: MatchResult,
    func: MatchResult,):

    do = do.result.display
    func = func.result.display


    if do in ("开启","enable"):
        do = "enable"
    elif do in ("关闭","disable"):
        do = "disable"
    elif do in ("状态","status"):
        do = "status"

    funcname = ""
    if func in ("-EarthQuack","地震通知"):
        func = "eq"
        funcname = "地震通知推送"
        
    member = await app.get_member(
        group=group,
        member_id=event.sender.id
    )

    if member.permission == "MEMBER" or event.sender.id not in config.owners:
        await app.send_group_message(
            target=group,
            message=MessageChain(
                Plain(f"您的权限不足，请联系群管理员以上权限者或机器人主人来操作此命令")
            )
        )
        return
    
    s = await change_sub_status(func,group=group.id,status=do)
    
    if s:
        await app.send_group_message(
            target=group,
            message=MessageChain(
                Plain(f"<{funcname}>已经在本群开启")
            )
        )
    else:
        await app.send_group_message(
            target=group,
            message=MessageChain(
                Plain(f"<{funcname}>已经在本群关闭")
            )
        )