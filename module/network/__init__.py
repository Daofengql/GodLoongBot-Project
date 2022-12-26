from graia.ariadne.model import Group
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Source
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    WildcardMatch,
    RegexMatch,
)

from .utils import pingip, tcpingip,dnsrecord,whois,aton

net = Channel.current()

net.name("网络插件")
net.author("道锋潜鳞")
net.description("网络功能插件")


@net.use(ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("net").help('群聊控制'),
                    UnionMatch(
                        "-ping",
                        "-tcping",
                        "-dns",
                        "-whois",
                        "-aton"
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
    group: Group,
    func: MatchResult,
    addr: MatchResult,
    port: MatchResult
):
    func = func.result.display
    addr = addr.result.display
    port = port.result.display

    try:
        if func == "-ping":
            rely = await pingip(addr)
        elif func == "-tcping" and port:

            rely = await tcpingip(addr,port)
        elif func == "-dns":
            rely = await dnsrecord(addr,port)

        elif func == "-whois":
            rely = await whois(addr)

        elif func == "-aton":
            rely = await aton(addr)

        else:
            rely = "很抱歉，未知的操作"
    except:
        rely = "操作异常"

    await app.send_group_message(
        target=group,
        quote=message.get_first(Source),
        message=rely
    )

        
