import asyncio
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
import aiocache
import PIL.Image as PImage
from io import BytesIO
from graia.ariadne.app import Ariadne

PATH = Path(__file__).parent / "assets"
   
from library.ToThread import run_withaio

@aiocache.cached(ttl=600)
async def genRankPic(lists,group,types:str) -> bytes:
    column = Column(Banner(f"位面[{group}]排行榜"))
    if types in ("", "综合排名"):
        column.add(Header("综合排名 换算综合得分排列", "按(能量币x10 + 合金x15000 + 凝聚力x5)/10000 计算 每10分钟刷新一次"))
    elif types == "能量币排行":
        column.add(Header("能量币排名", "每10分钟刷新一次"))
    elif types == "合金排行":
        column.add(Header("合金排名", "每10分钟刷新一次"))
    elif types == "凝聚力排行":
        column.add(Header("凝聚力排名", "每10分钟刷新一次"))

    for count, user in enumerate(lists, start=1):
        co = (user.coin*10 + user.iron*15000 + user.unity*5)/10000
        box1 = GeneralBox()
        box1.add(f"{count}、{user.nickname}", f"战..啊不，先驱{user.id}号 -- {co}分")
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
    rendered_bytes = await run_withaio(mock.render_bytes,args=())
    return rendered_bytes


@aiocache.cached(ttl=1800)
async def genSignPic(
    group:int, nickname:str, coin:int, iron:int, unity:int,id:int,qqid:int
) -> bytes:
    session = Ariadne.service.client_session
    async with session.get(f"https://v1.loongapi.com/v1/bot/stellairs/species/card/image?name={nickname}&id={id}&cash={coin}&alloys={iron}&unity={unity}&group={group}&qqid={qqid}") as resp:
        img = PImage.open(BytesIO(await resp.content.read()))
        b = BytesIO()
        img.save(b,format="PNG")
        b.seek(0)
        return b.read()