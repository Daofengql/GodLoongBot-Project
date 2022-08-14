from library.orm.extra import mysql_db_pool
from library.image.oneui_mock.elements import *
from library.orm.table import Sign_in
from library.config import config
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.model import Group
from graia.ariadne.message.element import At,Image,Face,Source
from .create import generatePicture
import httpx
from graia.ariadne.message.parser.twilight import (
    Twilight,
    RegexMatch
)
import datetime
import random
from sqlalchemy import select,insert
import asyncio
import json
from PIL import Image as PIYAN



signin = Channel.current()
signin.name("签到插件")
signin.author("道锋潜鳞")
signin.description("签到")


coin_range,coin_range2=(200,600)

db = mysql_db_pool()

@signin.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch(r"^(鳞|麟)币查询$")
                ]
            )
        ]
        )
    )
async def auth(
    app: Ariadne,
    event:GroupMessage,
    group: Group):
    dbsession = await db.get_db_session()
    try:
        async with dbsession() as session:
            result = await session.execute(
                select(
                    Sign_in
                    ).where(
                        Sign_in.qq==event.sender.id
                        ).limit(1)
                )
            result = result.scalars().all()
            if not result:
                await app.send_group_message(
                    group,
                    MessageChain(
                        At(event.sender),
                        f"您好像还没使用{config.name}签到或者充值过嗷，要不发送  签到   试试看吧",
                        Face(277),
                        Face(277),
                        Face(277)
                        )
                )
                return
            result = result[0]
            await app.send_group_message(
                    group,
                    MessageChain(
                        At(event.sender),
                        f"\n尊敬的{result.id}号用户\n！！查询成功！！\n您的麟币余额为：{result.coin} \n请再接再厉",
                        Face(277),
                        Face(277),
                        Face(277),
                        Face(277)
                        )
                )
            return
    except:
        await app.send_group_message(
                    group,
                    MessageChain(At(event.sender),f"啊欧，出错了，暂时找不到你的麟币了~QWQ~\n但是没有关系，它们应该还在{config.name}的仓库里面")
                )
        return

async def checktime(result:Sign_in):
    nowtime = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")
    return (nowtime - result.lastdate)> datetime.timedelta(seconds=4)

async def get_minyan()->str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
    try:
        async with httpx.AsyncClient() as client:response1 = await client.get("https://api.s1.hanwuss.com/tools/et/minyan", headers = headers)
    except:return '道可道，非常道'
    else:data = json.loads(response1.text)
    return data['content'] +'---'+ data['author']
    
    
async def geimage(qq,name,coin,days,minyan):
    back = await asyncio.gather(
        asyncio.to_thread(
            generatePicture,
            qq,
            name,
            coin,
            days,
            ""
        )
    )
    img = PIYAN.open(back[0])
    box = GeneralBox()
    column = Column(Banner("签到"), Header("签到成功", "希望你能够再接再厉哦"))
    column.add(img)
    box.add(f"鳞币余额：{coin}","麟币可用于商城兑换，以及特殊功能的使用")
    box.add(f"签到天数：{days}","您已经签到的天数")
    box.add(minyan,"")
    column.add(box)
    mock = OneUIMock(column)
    rendered_bytes = await asyncio.gather(asyncio.to_thread(mock.render_bytes))
    rendered_bytes= rendered_bytes[0]
    return rendered_bytes

@signin.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch(r"^签到$")
                ]
            )
        ]
        )
    )
async def sign(
    app: Ariadne,
    event:GroupMessage,
    group: Group):
    dbsession = await db.get_db_session()
    minyan= await get_minyan()
    name = await app.get_user_profile(event.sender.id)
    await app.send_message(
        group,
        MessageChain(
            f"来了来了,{config.name}给你登记下，客官稍等"
        )
    )
    
    try:
        async with dbsession() as session:
            b = await session.execute(select(Sign_in).where(Sign_in.qq==int(event.sender.id)).with_for_update().limit(1))
            b = b.scalars().all()
            if b:
                b:Sign_in = b[0]
                if await checktime(b):
                    b.lastdate = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")
                    coinincrease = random.randint(coin_range,coin_range2)
                    b.coin += coinincrease
                    b.days += 1
                    
                    image = await geimage(event.sender.id,name.nickname,b.coin,b.days,minyan)
                    
                    
                    await app.send_group_message(
                        group,
                        MessageChain(Image(data_bytes=image)),
                        quote =event.message_chain.get_first(Source)
                    )
                    await session.commit()
                    return
                else:
                    await app.send_group_message(
                        group,
                        MessageChain('你说有没有一种可能，你今天已经签到过了呢'),
                        quote =event.message_chain.get_first(Source)
                    )
                    return
            else:
                coinincrease= 2*random.randint(coin_range,coin_range2)
                await session.execute(insert(Sign_in).values(qq=int(event.sender.id),
                            lastdate = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S"),
                            days=1,
                            coin = int(coinincrease)))
                image = await geimage(event.sender.id,name.nickname,coinincrease,1,minyan)
                await session.commit()
                await app.send_group_message(
                    group,
                    MessageChain(
                        Image(data_bytes=image),
                        '这是您第一次使用签到功能，系统给您两倍的签到奖励，往后的日子还望多多关照，祝您生活愉快'
                    ),
                    quote =event.message_chain.get_first(Source)
                )
                return
                
    except Exception as e:
        await app.send_group_message(
                        group,
                        MessageChain(At(event.sender.id),'  啊嗷，签到可能失败惹，等会再试试看吧'),
                        quote =event.message_chain.get_first(Source)
                    )
        return