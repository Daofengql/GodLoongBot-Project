
from library.orm.table import User
from library.Bot import bot
from library.orm.extra import mysql_db_pool
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, At, Plain, Source
from graia.ariadne.model import Group
from graia.broadcast.interrupt import Waiter, InterruptControl
import os
import random
import datetime
import re
import asyncio

from .generation import (
    genSignPic,
    genRankPic,
)
import uuid

from library.vault import dbexec




dbexe  = dbexec()

pattern = re.compile(r'[\u4e00-\u9fa5A-Za-z0-9^=?$\x22.]+')
db = mysql_db_pool()
PATH = os.path.dirname(__file__) + "/assets/"

bot = bot()

energy_range = [100, 500]



# 检查时间
async def checktime(result: User) -> bool:
    return (
        datetime.datetime.strptime(
            datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"), "%Y-%m-%d %H:%M:%S"
        )
        - result.lasttime
    ) > datetime.timedelta(seconds=4)

async def getRandSpecies():
    session = Ariadne.service.client_session
    try:
        async with session.get("https://v1.loongapi.com/v1/bot/stellairs/species/random") as resp:
            id = (await resp.json())["result"]["id"]
    except:
        id = 0
    return id    




# 检查时间是否在夜间保护时间内
async def checktimeIfInNight() -> bool :
    now = datetime.datetime.now()
    start_time = datetime.datetime.strptime(str(now.date()) + '23:50', '%Y-%m-%d%H:%M')
    end_time = start_time + datetime.timedelta(minutes=10)
    if start_time < now < end_time: return True
    start_time = datetime.datetime.strptime(str(now.date()) + '00:00', '%Y-%m-%d%H:%M')
    end_time = start_time + datetime.timedelta(hours=1)
    if start_time <= now <= end_time: return True
    return False



# 签到
async def DailySignin(
    app: Ariadne,
    group: Group,
    event: GroupMessage
) -> MessageChain:
    """进行签到获取积分"""

    

    ##判断是否正在使用
    if await checktimeIfInNight():
        return MessageChain(
            Plain("在当日23:50分至次日1时之间，签到功能将暂使用。系统将在后台统计签到数据")
        )
    user = await dbexe.getUserProfile(event.sender.id,group.id)
    if user :
        coinincrease = random.randint(energy_range[0], energy_range[1])
        user = user[0]
        if not await checktime(user):
                return MessageChain(
                    Plain(
                        f"先驱 [{event.sender.name}] ,您今天已经在位面：{group.id}上领取过您的今日奖励了，请使用其他方法获取麟币。今天就别再在这签到了，小心首星变黑洞（"
                    )
                )
        await dbexe.modifyUserProfile(
            qq = event.sender.id,
            group = group.id,
            nickname=user.nickname,
            coin = user.coin + coinincrease,
            unity = user.unity,
            species = user.species,
            iron = user.iron 

        )

        img = await genSignPic(
            user.group,
            user.nickname,
            user.coin + coinincrease,
            user.iron,
            user.unity,
            user.species
        )
    else:
        asyncio.create_task(
            app.send_group_message(
                target=group,
                message=MessageChain(
                        Plain("新的链接已接入~~~\n检测到《SOL "),
                        Plain("🌐"),
                        Plain(
                            f""" III》上的土著...啊不，先驱（{
                            event.sender.name
                        }）研究出了空间飞行技术\n正在为ta申请加入星海共同体....."""
                        ),
                    ),
                quote=event.message_chain.get_first(Source),
            ),
                name=uuid.uuid4()
            )
        species = await getRandSpecies()
        try:
            name = str(pattern.search(event.sender.name.strip()).group())[:15]
        except:
            name = "UNKNOWN-User"
        coinincrease = 2 * random.randint(energy_range[0], energy_range[1])
        await dbexe.insertUserProfile(
            qq = event.sender.id,
            group = group.id,
            nickname=name,
            coin=coinincrease,
            unity= 100,
            species=species
        )
        img = await genSignPic(
                group.id,
                name,
                coinincrease,
                0,
                100,
                species
            )

    return MessageChain(Image(data_bytes=img))


# 获取信息
async def getMyInfo(
    group: Group,event: GroupMessage
) -> MessageChain:
    """获取自身资源数据"""
    first = await dbexe.getUserProfile(event.sender.id,group.id)
    if not first:
        return MessageChain(
            Plain(
                "您还没在本位面进行签到，请发送签到进行注册"
            )
        )
    first = first[0]
    img = await genSignPic(
            first.group,
            first.nickname,
            first.coin,
            first.iron,
            first.unity,
            first.species
        )
    return MessageChain(Image(data_bytes=img))


# 获取群排行
async def getGroupRank(
    app: Ariadne, group: Group, types: str
) -> MessageChain:
    """获取群排行榜"""
    asyncio.create_task(
        app.send_group_message(group, f"正在获取位面[{group.id}]的排名"),
        name=uuid.uuid4()
            )
    lists = await dbexe.getGroupRank(group.id,types)
    img = await asyncio.create_task(genRankPic(lists,group.id, types),name=uuid.uuid4())
    return MessageChain(Image(data_bytes=img))


convertList = []
#兑换合金
async def convertAssets(
    app: Ariadne, group: Group, event: GroupMessage, params
)-> MessageChain:
    if f"{event.sender.id}:{group.id}" in convertList:
        return MessageChain("当前您有一个兑换任务等待完成 如需退出请发送 退出兑换")
    convertList.append(f"{event.sender.id}:{group.id}")
    first = await dbexe.getUserProfile(event.sender.id,group.id)
    if not first:
        convertList.remove(f"{event.sender.id}:{group.id}")
        return MessageChain(
            Plain(
                f"守望者【{event.sender.id}】 位面【{group.id}】的星海中没有您的登记，请使用\n.Galaxy -Signin 或 逐鹿星河 签到\n来注册您的星海账号！"
            )
        )

    if params == "合金":
        await app.send_group_message(
            group,
            "《泛星系市场》\n请问您需要兑换多少合金呢  每1合金需要1500能量币 请在30秒内回复"
        )
        @Waiter.create_using_function(listening_events=[GroupMessage])
        async def waiter(waiter_message: MessageChain, g: Group, e: GroupMessage):
            if e.sender.id == event.sender.id and g.id == group.id:
                if waiter_message.display == "退出兑换":
                    convertList.remove(f"{event.sender.id}:{group.id}")
                    return False,0
                if waiter_message.display.isdigit():
                    if int(waiter_message.display) >0:
                        convertList.remove(f"{event.sender.id}:{group.id}")
                        return True,int(waiter_message.display)
                    else:
                        convertList.remove(f"{event.sender.id}:{group.id}")
                        return False,0

        try:
            status, dat = await asyncio.wait_for(
                InterruptControl(app.broadcast).wait(waiter), 30
            )
        except asyncio.exceptions.TimeoutError:
            convertList.remove(f"{event.sender.id}:{group.id}")
            return MessageChain("超时拉~")
        
        if not status:
            return MessageChain("已退出兑换 或 您的输入有误")
        
        first: User = first[0]
        if first.coin < dat*1500:
            return MessageChain("兑换失败， 你的能量币剩余不足以兑换")

        await dbexe.modifyUserProfile(
            qq = event.sender.id,
            group = group.id,
            nickname=first.nickname,
            coin = first.coin - 1500*dat,
            unity = first.unity,
            species = first.species,
            iron = first.iron + dat 

        )

        return MessageChain(f"兑换成功，消耗{dat*1500}能量币兑换了{dat}合金")



#崇拜
async def worShip(    
    app: Ariadne, group: Group, event: GroupMessage, message:MessageChain
) -> MessageChain:
    """崇拜获取凝聚力"""
    if not message.has(At):
        return MessageChain("好像没有要崇拜的对象哦")
    return MessageChain("功能开发中")



#改名
async def changeMyName(    
    group: Group, event: GroupMessage
) -> MessageChain:
    """刷新数据库中的名字"""
    first = await dbexe.getUserProfile(event.sender.id,group.id)
    if not first:
            return MessageChain("本星海中没有您的记录，请使用   逐鹿星河 签到   或   .Galaxy -Signin   来注册您的账号")
    first: User = first[0]
    name = str(pattern.search(event.sender.name.strip()).group())
    name = name[:15]
    await dbexe.modifyUserProfile(
            qq = event.sender.id,
            group = group.id,
            nickname=name,
            coin = first.coin,
            unity = first.unity,
            species = first.species,
            iron = first.iron 

        )

    return MessageChain("您在本星海的昵称已经跟具当前群昵称刷新")
        



    