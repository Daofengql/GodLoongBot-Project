from graia.ariadne.model import Group
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Source,Image,Plain
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    WildcardMatch,
    RegexMatch,
    ArgumentMatch
)

from .utils import searchFromPage,WaitForResp,getBT

et = Channel.current()

et.name("娱乐插件")
et.author("道锋潜鳞")
et.description("娱乐功能插件")


@et.use(ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("#种子",".bt","!bt","#bt").help('群聊控制'),
                    ArgumentMatch("-f",optional=True) @ "func",
                    WildcardMatch() @ "target"
                ]
            )
        ]
    )
)
async def etmod(
    app: Ariadne,
    message: MessageChain,
    group: Group,
    event: GroupMessage,
    func: MatchResult,
    target: MatchResult,
):
    if func.matched:
        func = func.result.display
    else:
        func = "search"

    if target.matched:
        target = target.result.display
    else:
        target = ""

    
    if func == "search" and target:
        pic,pages = await searchFromPage(target)
        await app.send_group_message(
            target=group,
            message=MessageChain(
                Image(data_bytes=pic)
            ),
            quote=message.get_first(Source)
        )
        choice = await WaitForResp(app,group,event,message)
        if int(choice) > len(pages):
            await app.send_group_message(
                target=group,
                message="回复好像不规范哦",
                quote=message.get_first(Source)
            )
            return
        
        ret = await getBT(app,group,message.get_first(Source),pages[int(choice)-1])

    else:
        await app.send_group_message(
            target=group,
            message="功能异常，参数不完整，请检查参数",
            quote=message.get_first(Source)
        )
        return

    await app.send_group_message(
            target=group,
            message=ret,
            quote=message.get_first(Source)
        )
    return