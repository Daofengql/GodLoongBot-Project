from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Source
from graia.ariadne.message.parser.twilight import (MatchResult, RegexMatch,
                                                   Twilight, UnionMatch,
                                                   WildcardMatch)
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from .utils import (ShodanSearchIP, ShodanSearchQuery, aton, dnsrecord, pingip,
                    tcpingip, whois)

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
                        "-aton",
                        "-ShodanIP"
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
    port: MatchResult,
    source:Source
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

        elif func == "-ShodanIP":
            rely = await ShodanSearchIP(addr)

        else:
            rely = "很抱歉，未知的操作"
    except Exception as e:
        rely = "操作异常"

    await app.send_group_message(
        target=group,
        quote=source,
        message=rely
    )

        
@net.use(ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("net").help('群聊控制'),
                    UnionMatch(
                        "-shodan"
                        ),
                    WildcardMatch() @ "query"
                ]
            )
        ]
    )
)
async def pingmod(
    app: Ariadne,
    message: MessageChain,
    group: Group,
    query: MatchResult,
    source:Source
):

    query = query.result.display

    try:
        rely = await ShodanSearchQuery(query)
    except Exception as e:
        rely = "操作异常"

    await app.send_group_message(
        target=group,
        quote=source,
        message=rely
    )
