from library.config import config
from library.orm.table import User
from library.Bot import bot


from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, At, Plain, Source
from graia.ariadne.model import Group
from graia.broadcast.interrupt import Waiter, InterruptControl

from pymysql import err

import os
from sqlalchemy import select, insert
import random
import datetime

import asyncio

from .generation import (
    genSignPic,
    genRankPic,
)


from .utils import db


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


# 签到
async def DailySignin(
    app: Ariadne,group: Group,event: GroupMessage,
) -> MessageChain:
    """进行签到获取积分"""
    ##判断是否正在使用
    detail = await event.sender.get_profile()
    avatar = await event.sender.get_avatar()
    dbsession = await db.get_db_session()
    async with dbsession() as session:
        # 读取用户是否存在
        first = await session.execute(
            select(User)
            .where(User.qq == event.sender.id, User.group == group.id)
            .with_for_update()
            .limit(1)
        )
        first = first.scalars().all()
        if not first:
            # 如果不存在，则添加新用户
            await app.send_group_message(
                group,
                MessageChain(
                    Plain("新的链接已接入~~~\n检测到《SOL "),
                    Plain("🌐"),
                    Plain(
                        f""" III》上的土著...啊不，先驱（{
                        event.sender.name
                    }）研究出了空间飞行技术\n正在为ta申请加入星海共同体....."""
                    ),
                ),
                quote=event.message_chain.get_first(Source),
            )

            # 开始加入数据库
            coinincrease = 2 * random.randint(energy_range[0], energy_range[1])
            await session.execute(
                insert(User).values(
                    qq=event.sender.id,
                    group=group.id,
                    lasttime=datetime.datetime.strptime(
                        datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"),
                        "%Y-%m-%d %H:%M:%S",
                    ),
                    coin=coinincrease,
                    nickname=event.sender.name,
                    iron=0,
                    unity=100,
                )
            )
            
            img = await genSignPic(
                detail.age,
                detail.sex,
                avatar,
                group.id,
                event.sender.name,
                coinincrease,
                "",
                0,
                100,
                "我们的征途是星辰大海",
                "此刻，众神踏入英灵殿！",
                True,
            )

        else:
            first: User = first[0]
            if not await checktime(first):
                return MessageChain(
                    Plain(
                        f"先驱 [{event.sender.name}] ,您今天已经在位面：{group.id}上领取过您的今日奖励了，请使用其他方法获取麟币。梵天神兵都没你高效（"
                    )
                )
            # 修改当前时间
            first.lasttime = datetime.datetime.strptime(
                datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"),
                "%Y-%m-%d %H:%M:%S",
            )
            # 增加鳞币
            coinincrease = random.randint(energy_range[0], energy_range[1])
            first.coin += coinincrease
            if coinincrease > 0:
                s = f"{first.coin}  ↑{coinincrease}"
            else:
                s = f"{first.coin}  ↓{coinincrease}"

            # 开始绘图
            img = await genSignPic(
                detail.age,
                detail.sex,
                avatar,
                first.group,
                first.nickname,
                s,
                "",
                first.iron,
                first.unity,
                "我们的征途是星辰大海",
                "欢迎回来，我们的先驱!",
                False,
            )

        await session.commit()
        return MessageChain(Image(data_bytes=img))


# 获取信息
async def getMyInfo(
    app: Ariadne,group: Group,event: GroupMessage,
) -> MessageChain:
    """获取自身资源数据"""
    detail = await event.sender.get_profile()
    avatar = await event.sender.get_avatar()
    await app.send_group_message(group, "Situation Log Updated ...... Waitting.....")
    dbsession = await db.get_db_session()
    async with dbsession() as session:
        first = await session.execute(
            select(User)
            .where(User.qq == event.sender.id, User.group == group.id)
            .with_for_update()
            .limit(1)
        )
        first = first.scalars().all()
        if not first:
            return MessageChain(
                Plain(
                    f"守望者【{event.sender.id}】 位面【{group.id}】的星海中没有您的登记，请使用\n.Galaxy -Signin 或 逐鹿星河 签到\n来注册您的星海账号！"
                )
            )
        first: User = first[0]
        if not first:
            return MessageChain(Plain("本群好像还没加入星海~"))
        img = await genSignPic(
            detail.age,
            detail.sex,
            avatar,
            first.group,
            first.nickname,
            first.coin,
            "",
            first.iron,
            first.unity,
            f"星海{group.id}----{event.sender.id}",
            "",
            False,
        )
        return MessageChain(Image(data_bytes=img))


# 获取群排行
async def getGroupRank(
    app: Ariadne, group: Group, types: str
) -> MessageChain:
    """获取群排行榜"""
    await app.send_group_message(group, f"正在获取位面[{group.id}]的排名")

    img = await genRankPic(group.id, types)
    return MessageChain(Image(data_bytes=img))


convertList = []
#兑换合金
async def convertAssets(
    app: Ariadne, group: Group, event: GroupMessage, params
)-> MessageChain:
    if f"{event.sender.id}:{group.id}" in convertList:
        return MessageChain("当前您有一个兑换任务等待完成 如需退出请发送 退出兑换")
    convertList.append(f"{event.sender.id}:{group.id}")
    try:
        dbsession = await db.get_db_session()
        async with dbsession() as session:
            first = await session.execute(
                select(User)
                .where(User.qq == event.sender.id, User.group == group.id)
                .with_for_update()
                .limit(1)
            )
            first = first.scalars().all()
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
                
                first.coin = first.coin - 1500*dat
                first.iron = first.iron + dat

                await session.commit()
                return MessageChain(f"兑换成功，消耗{dat*1500}能量币兑换了{dat}合金")

    except err.DataError: 
        return MessageChain("目标上行计算机操作异常，可能是因为您宛如神明，资源爆仓，导致无法兑换")
        
    except err.DatabaseError:
        return MessageChain("目标上行计算机操作异常，请稍后再试")

    except Exception:
        return MessageChain("目标上行计算机发生未知故障，请稍后再试")


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
    name = event.sender.name
    dbsession = await db.get_db_session()
    async with dbsession() as session:
        first = await session.execute(
            select(User)
            .where(User.qq == event.sender.id, User.group == group.id)
            .with_for_update()
            .limit(1)
        )
        first: list[User] = first.scalars().all()
        if not first:
            return MessageChain("本星海中没有您的记录，请使用   逐鹿星河 签到   或   .Galaxy -Signin   来注册您的账号")
        first: User = first[0]
        first.nickname = name
        await session.commit()
        return MessageChain("您在本星海的昵称已经跟具当前群昵称刷新")


        



    