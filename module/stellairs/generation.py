import asyncio
from io import BytesIO
from pathlib import Path

import PIL.Image as PImage

from library.image.oneui_mock.elements import (
    Banner,
    Header,
    MenuBox,
    GeneralBox,
    Column,
    OneUIMock,
)
from library.orm.table import User
import aiocache

import random
from .texts import MINYAN
from sqlalchemy import select

from library.orm.extra import mysql_db_pool
db = mysql_db_pool()

PATH = Path(__file__).parent / "assets"

NEW_USER = """
I solemny swear \n
我在这里庄严起誓\n
To devote my life end of realease in defense of the united nations of earth. \n
我此生将不遗余力，用以保护地球联合国\n
To defend the Constitution of the man and to further the universal rights of all sentient life .\n
保护人类火种的延续，以及星空所有有知生命\n
From the depths of the Pacific ，to the edge of the Galaxy.\n
无论从太平洋深处，还是到银河系的边缘\n
For as long as I shall live.\n
至死方休！！
"""


# 生成信息图片
@aiocache.cached(ttl=1800)
async def genSignPic(
    age:int,sex:str,avatar:bytes, group:int, nickname:str, coin:int, ev, iron:int, unity:int, banner:str, header:str, isnew:bool
) -> bytes:
    if not header:
        header = random.choice(MINYAN)
    imageio = BytesIO()
    
    column = Column(Banner(banner), Header(header, ""))
    box1 = GeneralBox()
    box2 = GeneralBox()
    box3 = MenuBox()
    box4 = GeneralBox()
    imageio.write(avatar)
    imageio.seek(0)
    img = PImage.open(imageio)
    column.add(img)
    box1.add("您的信息如下：", "")

    box2.add(f"SOL III {group}位面的先驱", "")
    box2.add(f"Name:{nickname}", "")
    box2.add(f"Age:{age}", "")
    box2.add(f"Sex:{sex}", "")

    box3.add(
        f"麟币(能量币)：{coin}", "能量币可用于兑换合金", icon=PImage.open(PATH / "coins" / "Energy.png")
    )
    if ev:
        box3.add("麟币(能量币)事件：", ev)
    box3.add(f"合金：{iron}", "合金可用于购买舰船", icon=PImage.open(PATH / "coins" / "Alloys.png"))
    box3.add(
        f"凝聚力：{unity}", "您在本群的威望 默认为100", icon=PImage.open(PATH / "coins" / "Unity.png")
    )
    if isnew:
        box4.add(NEW_USER, "")
    column.add(box1, box2, box3, box4)
    mock = OneUIMock(column)
    rendered_bytes = await asyncio.gather(asyncio.to_thread(mock.render_bytes))
    rendered_bytes = rendered_bytes[0]
    return rendered_bytes

@aiocache.cached(ttl=600)
async def genRankPic(group,types:str) -> bytes:
    lists = await _getGroupRank(group,types)
    column = Column(Banner(f"位面[{group}]排行榜"))
    if types in ("", "综合排名"):
        column.add(Header("综合排名", "按能量币x35% 合金x60% 凝聚力x5% 排列"))
    elif types == "能量币排行":
        column.add(Header("能量币排名", ""))
    elif types == "合金排行":
        column.add(Header("合金排名", ""))
    elif types == "凝聚力排行":
        column.add(Header("凝聚力排名", ""))

    for count, user in enumerate(lists, start=1):
        box1 = GeneralBox()
        box1.add(f"{count}、{user.nickname}", f"战..啊不，先驱{user.id}号")
        box2 = MenuBox()
        box2.add(
            f"麟币(能量币)：{user.coin}",
            "能量币可用于兑换合金",
            icon=PImage.open(PATH / "coins" / "Energy.png"),
        )
        box2.add(
            f"合金：{user.iron}",
            "合金可用于购买舰船",
            icon=PImage.open(PATH / "coins" / "Alloys.png"),
        )
        box2.add(
            f"凝聚力：{user.unity}",
            "您在本群的威望 默认为100",
            icon=PImage.open(PATH / "coins" / "Unity.png"),
        )
        column.add(box1, box2)

    mock = OneUIMock(column)
    rendered_bytes = await asyncio.gather(asyncio.to_thread(mock.render_bytes))
    rendered_bytes = rendered_bytes[0]
    return rendered_bytes


@aiocache.cached(ttl=600)
async def _getGroupRank(
    group, types
) -> list[User]:
    dbsession = await db.get_db_session()
    async with dbsession() as session:
        if types in ("", "综合排名"):
            first = await session.execute(
                select(User)
                .where(User.group == group)
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
    return first