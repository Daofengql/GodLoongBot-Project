from library.tcping import tcping
from library.image.oneui_mock.elements import *
from graia.ariadne.model import Group
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.base import MatchRegex
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.broadcast.interrupt import Waiter, InterruptControl
from graia.ariadne.message.element import At, Plain, Image, Forward, ForwardNode
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    ArgumentMatch,
    ArgResult,
    WildcardMatch,
    RegexMatch,
    ParamMatch,
)
import asyncio
import random
from datetime import datetime
import socket,httpx
from ping3 import ping as p

import json,re
import aiohttp

ping = Channel.current()

ping.name("Ping插件")
ping.author("道锋潜鳞")
ping.description("通过服务器调用socket来实现ping")


pattern = re.compile(r'[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?')

def pings(args):
    try:  ip_address = socket.gethostbyname(args)
    except:   return {"host":args,"ip":args,"code":"1","delay":"错误的地址没法解析"}
    else:
        response = p(ip_address)
        if response is not None: return {"host":args,"ip":ip_address,"delay":str(int(response * 1000))+"ms","code":"0"}
        else:  return {"host":args,"ip":ip_address,"delay":"超时或禁ping","code":"1"}
            
            
async def ipinfo(args):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
    url = f"https://api.s1.hanwuss.com/tools/net/ip/address?ip={args}"
    try:
        async with httpx.AsyncClient() as client:   response1 = await client.get(url, headers = headers)
    except:  return {"code":0,"Msg":"查询失败"}
    else:  return {"code":1,"Msg":"成功","data":json.loads(response1.text)["info"]}

@ping.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchRegex(regex=r"^ping [a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?")]
        )
    )
async def pingip(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    args = str(message.display).strip()[5:]
    pingw = pings(args)
    info = await ipinfo(pingw['ip'])
    if info["code"]:
        try:
            addr = info["data"]["country"]
            city = info["data"]["isp"]
        except:addr = city = "查询失败"
    else:addr = city = "查询失败"
    rely = f"\nIP/域名：{pingw['host']}\n响应ip：{pingw['ip']}\n延迟：{pingw['delay']}\n物理地址：{addr}\nISP：{city}"
    await app.send_message(
             group,
            MessageChain(At(event.sender),rely)
         )
         
         
tpi = tcping() 
         
@ping.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchRegex(regex=r"^tcping [a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.? [0-9]{1,5}")]
        )
    )
async def tcpingip(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    host,port = str(message.display.strip()[7:]).split(" ")
    
    time = tpi.tcping(host,int(port))#取得端口延迟
    #解析域名或ip得到实际ip
    try:ip_address = socket.gethostbyname(host)
    except:ip_address ="解析失败"
    if abs(time) >=20000:time = "tcping超时"
    else:time = f"{time}ms"
    
    info = await ipinfo(ip_address)
    if info["code"]:
        try:
            addr = info["data"]["country"]
            city = info["data"]["isp"]
        except:addr = city = "查询失败"
    else:addr = city = "查询失败"
    
    
    rely = f"\nIP/域名：{host}\n指向ip：{ip_address}\n端口:{port}\n延迟：{time}\n物理地址：{addr}\nISP：{city}"
    
    await app.send_group_message(
            group,
            MessageChain(At(event.sender),rely)
        )
        

@ping.use(ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(".dns","DNS查询").help('群聊控制'),
                    RegexMatch(r"[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?") @ "domain",
                    WildcardMatch() @ "ip"
                ]
            )
        ]
    )
)
async def dnsrecord(app: Ariadne,
    message: MessageChain,
    event:GroupMessage,
    group: Group, 
    domain: MatchResult, 
    ip: MatchResult
    ):
    ip = ip.result.display
    par = {"name":domain.result.display}
    
    
    box = GeneralBox()
    if ip and pattern.search(ip):
        par["edns_client_subnet"] = pattern.search(ip).group()
        box.add("使用了特定的公网地址查询解析", f"地址：{pattern.search(ip).group()}")
    
    
    column = Column(Banner("DNS查询"), Header("查询返回", "基于寒武天机的全球DOH检测网络返回数据"))
    
    session = Ariadne.service.client_session
    async with session.get('https://dns.alidns.com/resolve',params=par) as response:
        result = json.loads(await response.text())
        try:
            if result["code"]:box.add("检测错误", result["code"])
        except:pass
        try:
            for res in result["Answer"]:
                if res['type'] == 1:typ = "A"
                elif res['type'] == 5 :typ = "CNAME"
                elif res['type'] == 6 :typ = "NS"
                else:typ = "其他"
                box.add(f"响应：{res['data']}  TTL={res['TTL']}",f"上级节点：{res['name']} 解析类型：{typ}")
        except:box.add("检测错误","")
    column.add(box)
    mock = OneUIMock(column)
    rendered_bytes = await asyncio.gather(asyncio.to_thread(mock.render_bytes))
    rendered_bytes= rendered_bytes[0]
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=rendered_bytes))
         )