import asyncio
import datetime
import os
import zipfile
from pathlib import Path
from urllib import parse

import aiocache
import aiohttp
from io import BytesIO
from bs4 import BeautifulSoup
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.broadcast.interrupt import InterruptControl, Waiter
from lxml import etree
from copy import deepcopy
from library.minio import client, guess_content_type,minio_conf
from library.image.oneui_mock.elements import (Banner, Column, GeneralBox,
                                               Header, OneUIMock)
from library.ToThread import run_withaio

PATH = Path(os.getcwd()) / "cache" / "btget"

@aiocache.cached(ttl=3600)
async def getPage(url)->str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.text()
            else:
                return ""

@aiocache.cached(ttl=3600)
async def downloadBT(url)->bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.content.read()
            else:
                return ""

@aiocache.cached(ttl=3600)
async def parseFromPage(target)->list[tuple]:
    pg = await getPage(f"https://www.btbtt15.com/search-index-keyword-{target}.htm")

    if not pg:
        return 0

    page = BeautifulSoup(pg,"html.parser")
    rlist = page.find_all("table",class_="thread")
    ret = list()

    for a in rlist:
        p = BeautifulSoup(str(a),"html.parser")
        t = p.find("td",class_="subject").find_all("a")
        title = str()
        for a1 in t:
            title = title + a1.text
        href = t[-1].get("href")
        au = p.find("td",class_="username").find_all("span")
        auther = au[0].text + " - " + au[-1].text
        for keywords in ["综艺","动漫","电影","高清","剧集","图书"]:
            if keywords in title[:10]:
                ret.append((title,href,auther))
                break
    return ret
    
@aiocache.cached(ttl=3600)
async def parseBTFileFromPage(target)->list[tuple]:
    pg = await getPage("https://www.btbtt15.com/" + target)

    if not pg:
        return 0

    u = []
    page = BeautifulSoup(pg,"html.parser")
    rlists = page.find_all("div",class_="attachlist")
    for attach in rlists:

        p = BeautifulSoup(str(attach),"html.parser")
        t = p.find_all("tr")[2:]
        for tr in t:
            r = BeautifulSoup(str(tr),"html.parser")
            as_ = r.find_all("a")
            for a in as_:
                if ".torrent" in a.text:
                    url = str(a.get("href")).replace("dialog","download")
                    u.append((a.text,url))
    return u


@aiocache.cached(ttl=3600)
async def searchFromPage(target):
    results = await parseFromPage(target)
    if not results:
        return bytes()

    column = Column(Banner(f"对象[{target}]搜索结果"))
    column.add(Header("请按照序号回复相应节点来获取种子", "本数据来源：bt之家"))
    count = 0
    pages = []
    for title,href,auther in results:
        box = GeneralBox()
        box.add(f"{count+1}. {title}", f"{auther}")
        column.add(box)
        pages.append(href)
        count += 1
    
    mock = OneUIMock(column)
    rendered_bytes = await run_withaio(mock.render_bytes,args=())
    return rendered_bytes,pages


async def WaitForResp(app:Ariadne,group:Group,event:GroupMessage,message:MessageChain):

    @Waiter.create_using_function(listening_events=[GroupMessage])
    async def waiter(waiter_message: MessageChain, g: Group, e: GroupMessage):
        if e.sender.id == event.sender.id and g.id == group.id:
            return waiter_message

    try:
        dat:MessageChain = await asyncio.wait_for(
            InterruptControl(app.broadcast).wait(waiter), 800
        )
        return dat
    except asyncio.exceptions.TimeoutError:
        await app.send_message(group, MessageChain("超时拉~"))
        return MessageChain()



async def getBT(app:Ariadne,group:Group,quote,page):
    files = await parseBTFileFromPage( page)
    if files:
        await app.send_group_message(
            target=group,
            message="种子已获取，正在打包下载，完成后会为您提供外链",
            quote=quote
        )

    upath = Path(str(datetime.datetime.today().year)) /  str(datetime.datetime.today().month) / str(datetime.datetime.today().day) / str(group.id)
    strfile2 = upath / f"{page}.zip"

    zip = BytesIO()
    zip_file = zipfile.ZipFile(zip, 'w', zipfile.ZIP_DEFLATED)

    for filename,downloadURL in files:
        await asyncio.sleep(0.5)
        data = await downloadBT("https://www.btbtt15.com/" + downloadURL)
        zip_file.writestr(filename,data)
    zip_file.close()

    zip = zip.getvalue()
    zip_file = BytesIO(zip)
    

    await asyncio.to_thread(client.put_object,minio_conf["bucket"],str("temp/bt/"/strfile2),zip_file,len(zip))



    return "https://objectstorage.global.loongapi.com/GodLoongBot" + parse.quote(f"/temp/bt/{strfile2}")
    