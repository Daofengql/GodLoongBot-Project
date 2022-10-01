
from library.image.oneui_mock.elements import *
from graia.ariadne.model import Group
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import At, Image, Source, Plain
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    WildcardMatch,
    RegexMatch,
)
import asyncio
import json,re

from .utils import pingip, tcpingip

net = Channel.current()

net.name("网络插件")
net.author("道锋潜鳞")
net.description("网络功能插件")


pattern = re.compile(r'[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?')




@net.use(ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("net").help('群聊控制'),
                    UnionMatch(
                        "-ping",
                        "-tcping"
                        ) @ "func",
                    RegexMatch(r"[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?") @ "addr",
                    WildcardMatch() @ "port"
                ]
            )
        ]
    )
)
async def pingmod(
    app: Ariadne,
    message: MessageChain,
    event: GroupMessage,
    group: Group,
    func: MatchResult,
    addr: MatchResult,
    port: MatchResult
):
    func = func.result.display
    addr = addr.result.display
    port = port.result.display

    if func == "-ping":
        rely = await pingip(addr)
    elif func == "-tcping" and port:
        try:
            rely = await tcpingip(addr,port)
        except:
            rely = "很抱歉，tcping异常"
    else:
        rely = "很抱歉，未知的操作"

    await app.send_group_message(
        target=group,
        quote=message.get_first(Source),
        message=MessageChain(
            At(event.sender.id),
            Plain("\n--------------"),
            Plain(rely)
        )
    )

    
    

         
         

        

@net.use(ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("net -dns","DNS查询").help('群聊控制'),
                    RegexMatch(r"[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?") @ "domain",
                    WildcardMatch() @ "ip"
                ]
            )
        ]
    )
)
async def dnsrecord(app: Ariadne,
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