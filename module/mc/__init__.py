import aiomcrcon
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    WildcardMatch,
)
from graia.ariadne.model import Group
from graia.ariadne.message.element import At,Image
from library.depend import Permission, FunctionCall
from library.model import UserPerm
from library.TextToImg import TextToImage
import os,asyncio
from library.config import config

client = aiomcrcon.Client('42.51.48.131',20050,'Lzf926813..')
maker = TextToImage()

mc = Channel.current()

mc.name("MCCMD插件")
mc.author("道锋潜鳞")
mc.description("使用群消息作为终端执行shell命令")

@mc.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(".mc"),
                    WildcardMatch() @ "args"
                ]
            )
        ],
        decorators=[
            Permission.require(
                UserPerm.BOT_OWNER, MessageChain("权限不足，你需要来自 所有人 的权限才能进行本操作")
            ),
            FunctionCall.record(mc.module),
        ],
        )
    )
async def runmc(
    app: Ariadne,
    event:GroupMessage,
    group: Group,
    args: MatchResult):
    
    
    try:
        await client.connect()
        data,_ = await client.send_cmd(args.result.display)
        data = await asyncio.to_thread(maker.create_image,data,130)
        await app.send_message(
                group,
            MessageChain(Image(data_bytes=data))
            )

    except:
        await app.send_message(
             group,
            MessageChain(At(event.sender.id),f"系统命令执行错误了")
         )
        return
    await client.close()


