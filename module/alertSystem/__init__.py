import asyncio
import aiohttp
from collections import deque
from library.config import config

from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Image, At, Plain, Source, AtAll
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.event.mirai import MemberHonorChangeEvent
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

import time

from library.orm.extra import mysql_db_pool

db = mysql_db_pool()

from library.ComputerVisual import ApiConfig,ComputerVisual


from .data import get_sub_group, parse_eq_data, change_sub_status

aleater = Channel.current()
aleater.author("道锋潜鳞")
aleater.description("预警系统")
aleater.name("预警插件")


imgEvaConf = ApiConfig(
    Subscription="",
    region="eastasia"
)#图像审查模块继承


INIT_LIST = deque(maxlen=150)#地震数据列

async def Eqinit():

    global INIT_LIST
    async with aiohttp.ClientSession() as session:
        for _ in range(1,6):
            try:
                async with session.get("http://www.ceic.ac.cn/daochu/id:1") as response:
                    x1 = await response.text()
            except:pass
            else:break
        try:
            tmp = await parse_eq_data(x1)
            if tmp:
                INIT_LIST = tmp
        except:
            pass

asyncio.run(Eqinit())#地震数据预启动

@aleater.use(SchedulerSchema(timers.every_custom_seconds(120)))
async def every_minute_speaking(app: Ariadne):
    """
    地震预警系统
    """
    global INIT_LIST

    session = Ariadne.service.client_session

    subgroup = await get_sub_group("eq")
    
    for _ in range(1,6):
        try:
            async with session.get("http://www.ceic.ac.cn/daochu/id:1") as response:
                x2 = await response.text()
        except:pass
        else:break

    x2 = await parse_eq_data(x2)

    for i in x2:
        if i not in INIT_LIST:
            INIT_LIST.append(i)
            message = f"根据中国地震台网速报：{i['time']} 在 {i['addr']} （{i['longitude']}° {i['latitude']}°）发生里氏 {i['level']}级地震，震源深度{i['depth']}KM \n本数据来源中国地震台网，http://www.ceic.ac.cn，正式数据以官方通知为准"
            
            for group in subgroup:
                try:
                    await app.send_group_message(
                        target=group,
                        message=message
                    )
                except:pass


@aleater.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("消息订阅管理", ".sub").help("主控制器"),
                    UnionMatch(
                        "-EarthQuack","地震通知",
                        "-ImageEva","图像审查"
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
    """
    预警订阅功能开启关闭
    """
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
    elif func in ("-ImageEva","图像审查"):
        func = "ImgEva"
        funcname = "图像健康性审查"
        
    member = await app.get_member(
        group=group,
        member_id=event.sender.id
    )

    if member.permission == "MEMBER" and (event.sender.id not in config.owners):
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


@aleater.use(SchedulerSchema(timers.every_custom_hours(24)))
async def clear_user(app: Ariadne):
    """
    定时清除签到系统中失效的群聊
    """
    group = await app.get_group_list()
    g = [i.id for i in group]



    dbsession = await db.get_db_session()
    async with dbsession() as session:
        await session.execute(
            f"""DELETE FROM `users` WHERE `group` not  in {str(tuple(g))};"""
        )
        await session.commit()



@aleater.use(
    ListenerSchema(
        listening_events=[GroupMessage]
        )
    )
async def imgLook(
    bot: Ariadne,
    message: MessageChain,
    event:GroupMessage,
    group: Group):
    """
    审查主函数
    """

    groups = await get_sub_group("ImgEva")

    if group.id not in groups:
        return

    if message.has(Image):
        for image in message.get(Image):
            url = image.url
            await asyncio.sleep(1)
            try:
                imgEva = ComputerVisual.ImageExamination(imgEvaConf)
                result = await imgEva.request(url)
            
                if result.IsImageAdultClassified or result.IsImageRacyClassified:
                    await bot.send_group_message(
                        message=MessageChain(
                            At(event.sender.id),
                            Plain("您刚刚的消息疑似存在不健康内容，请按照群要求处理")
                        ),
                        target=group
                    )
                    return 
            except:
                pass

@aleater.use(
    ListenerSchema(
        listening_events=[MemberHonorChangeEvent]
        )
    )
async def MemberHonorChange(
    bot: Ariadne,
    event:MemberHonorChangeEvent,
    group: Group):
    if event.action == "achieve":
        message = MessageChain(
            Plain(f"恭喜{event.member.id}获得了{event.honor}~~~~")
        )
        await bot.send_group_message(
            target=group,
            message=message
        )
    return

