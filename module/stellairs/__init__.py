from library.config import config
from graia.ariadne.app import Ariadne
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    WildcardMatch,
)

from graia.saya import Channel
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import GroupRecallEvent
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
    worShip,
    changeMyName,
    convertAssets,
    authcode
)
import aiofiles
import asyncio
import random

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
                        "-ChangeMyInfo", "更新名字",
                        "-Convert","兑换",
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




    """
    capcode = await authcode(8)
    await asyncio.sleep(1)
    tmpmessageid = await app.send_group_message(
        group,
        MessageChain(
            Plain(f"当前操作需要人机验证，请在40秒内发送如下字符串：{capcode}")
        ),
        quote=message.get_first(Source)
    )

    #撤回终止命令检测
    @Waiter.create_using_function(listening_events=[GroupMessage])
    async def waiter(waiter_message: MessageChain, g: Group, e: GroupMessage):
        if e.sender.id == event.sender.id and g.id == group.id and waiter_message.display==str(capcode):
            return True
        elif g.id == group.id and (str(capcode) in waiter_message.display) and e.sender.id != event.sender.id:
            return False
    try:
        status = await asyncio.wait_for(
            InterruptControl(app.broadcast).wait(waiter), 40
        )
        #如果有撤回事件响应，则终止等待，return返回结束处理
        if not status:
            await asyncio.sleep(1)
            await app.send_group_message(
                group,
                MessageChain(
                    Plain(f"验证失败，您的签到行为疑似非法")
                ),
                quote=message.get_first(Source)
            )
            await asyncio.sleep(2)
            await app.recall_message(message=tmpmessageid.id,target=group)
            return


    except asyncio.exceptions.TimeoutError:
        #如果检测撤回超时则意味着等待结束，开始进行正式任务处理
        await app.send_group_message(
            group,
            MessageChain(
                Plain(f"验证超时")
            ),
            quote=message.get_first(Source)
        )
        await asyncio.sleep(3)
        await app.recall_message(message=tmpmessageid.id,target=group)
        return
    """

    #撤回终止命令检测
    @Waiter.create_using_function(listening_events=[GroupRecallEvent])
    async def waiter(e: GroupRecallEvent):
        if e.message_id == message.get_first(Source).id: return True
    try:
        status = await asyncio.wait_for(
            InterruptControl(app.broadcast).wait(waiter), 4
        )
        #如果有撤回事件响应，则终止等待，return返回结束处理
        if status:
            await app.send_group_message(
                group, 
                MessageChain(
                    Plain("用户撤回了命令，操作已终止")
                ),
                quote=message.get_first(Source)
            )
            return
    except asyncio.exceptions.TimeoutError:
        #如果检测撤回超时则意味着等待结束，开始进行正式任务处理
        pass


    aioHTTPsession = Ariadne.service.client_session

    #签到功能
    if func in ("-Signin", "获取今日能量币", "签到"):
        ret = await DailySignin(app, group, event)

    #获取用户自身信息
    elif func in ("-MyInfo", "我的信息"):   
        ret = await getMyInfo(app, group, event)

    #用户主动刷新数据库名字
    elif func in ("-ChangeMyInfo", "更新名字"):
        ret = await changeMyName(group, event)

    #崇拜获取凝聚力，开发中
    elif func in ("-Worhip","崇拜"):
        ret = await worShip(app, group, event,message)

    #泛星系贸易市场，进行资源兑换
    elif func in ("-Convert","兑换") and param in ("合金"):
        ret = await convertAssets(app, group, event,param)

    #获取综合排名，各项资源排名
    elif func in ("-LocalRank", "本星海排名") and param in (
        "",
        "综合排名",
        "能量币排行",
        "合金排行",
        "凝聚力排行",
    ):
        ret = await getGroupRank(app, group, param)

    #彩蛋，控制台功能恶搞
    elif func in ("~", "控制台"):
        async with aiofiles.open(PATH + "another/~.gif", "rb") as f:
            ret = MessageChain(
                Image(data_bytes=await f.read()), Plain(f"想啥呢，这是多人联机，哪来的💀第四天灾（")
            )

    #终止序列
    else:
        ret = MessageChain(f"啊哦，顾问{config.name}不知道您想干嘛")

    #规定ret变量为消息链返回参数，所有功能的结束都返回一个消息链赋值给ret用于状态显示
    await app.send_group_message(
        group, 
        ret,
        quote=message.get_first(Source)
    )
    #await asyncio.sleep(3)
    #await app.recall_message(message=tmpmessageid.id,target=group)
