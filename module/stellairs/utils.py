from library.config import config
from library.orm.table import User
from library.Bot import bot
from library.orm.extra import mysql_db_pool

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, At, Plain, Source
from graia.ariadne.model import Group

import asyncio
import os
from sqlalchemy import select, insert
import random
import datetime

from .texts import *
from .generation import (
    genSignPic,
    genRankPic,
)


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


# 签到
async def DailySignin(
    app: Ariadne,
    group: Group,
    event: GroupMessage,
) -> MessageChain:
    """进行签到获取积分"""
    ##判断是否正在使用

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
                event,
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
                event,
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
    app: Ariadne,
    group: Group,
    event: GroupMessage,
) -> MessageChain:
    """获取自身资源数据"""
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
            event,
            first.group,
            first.nickname,
            first.coin,
            "",
            first.iron,
            first.unity,
            f"星海{group.id}----{event.sender.id}",
            random.choice(MINYAN),
            False,
        )
        return MessageChain(Image(data_bytes=img))


# 获取群排行
async def getGroupRank(
    app: Ariadne, group: Group, event: GroupMessage, types: str
) -> MessageChain:
    """获取群排行榜"""
    await app.send_group_message(group, f"正在获取位面[{group.id}]的排名")
    dbsession = await db.get_db_session()
    async with dbsession() as session:
        if types in ("", "综合排名"):
            first = await session.execute(
                select(User)
                .where(User.group == group.id)
                .order_by(
                    (
                        (User.coin * 0.35) + (User.iron * 0.6) + (User.unity * 0.05)
                    ).desc()
                )
                .limit(6)
            )
        elif types in ("能量币排行"):
            first = await session.execute(
                select(User)
                .where(User.group == group.id)
                .order_by(User.coin.desc())
                .limit(6)
            )
        elif types in ("合金排行"):
            first = await session.execute(
                select(User)
                .where(User.group == group.id)
                .order_by(User.iron.desc())
                .limit(6)
            )
        elif types in ("凝聚力排行"):
            first = await session.execute(
                select(User)
                .where(User.group == group.id)
                .order_by(User.unity.desc())
                .limit(6)
            )
        first: list[User] = first.scalars().all()
        img = await genRankPic(group, first, types)
        return MessageChain(Image(data_bytes=img))


#崇拜
async def worShip(    
    app: Ariadne, group: Group, event: GroupMessage, message:MessageChain
) -> MessageChain:
    """崇拜获取凝聚力"""
    if not message.has(At):
        return MessageChain("好像没有要崇拜的对象哦")
    
