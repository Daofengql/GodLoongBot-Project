from library.config import config
from graia.ariadne.app import Ariadne
from library.orm.table import User
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
import asyncio
import os
from sqlalchemy import select, insert
from library.orm.extra import mysql_db_pool
import random
import datetime
from .texts import *
from .generation import (
    genSignPic,
    genRankPic,
)
import aiofiles

stellairs = Channel.current()

stellairs.name("模拟群星")
stellairs.author("道锋潜鳞")
stellairs.description("模拟stellaris，舰队挑战")

db = mysql_db_pool()
PATH = os.path.dirname(__file__) + "/assets/"

SIGNING = []

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
    if event.sender.id in SIGNING:
        return MessageChain("你好像正在使用本功能，请先使用完成")
    SIGNING.append(event.sender.id)

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
                    }）还没加入星海\n正在为您申请加入星海....."""
                    ),
                ),
                quote=event.message_chain.get_first(Source),
            )
            """
            # 等待用户输入昵称
            @Waiter.create_using_function(listening_events=[GroupMessage])
            async def waiter(waiter_message: MessageChain, g: Group, e: GroupMessage):
                if e.sender.id == event.sender.id and g.id == group.id:
                    for word in bot.weijingci:
                        if word in waiter_message.display: 
                            return False,""
                    return True,waiter_message.display

            try:
                stat,dat = await asyncio.wait_for(
                    InterruptControl(app.broadcast).wait(waiter), 30
                )
            except asyncio.exceptions.TimeoutError:
                SIGNING.remove(event.sender.id)
                return MessageChain("超时拉~")
            if not stat:
                await app.send_group_message(
                    group,
                    "您的昵称含有不适宜的词汇，已经暂停生成",
                ) 
                return
            
            #加入提醒
            await app.send_group_message(
                group,
                "正在为您制作星海共同体成员名片....",
                quote=event.message_chain.get_first(Source)
            )
            """
            await asyncio.sleep(random.randint(1, 4))  # 假装延迟（

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
                SIGNING.remove(event.sender.id)
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
        SIGNING.remove(event.sender.id)
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
