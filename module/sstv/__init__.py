from graia.ariadne.app import Ariadne
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    ArgumentMatch,
    WildcardMatch
)
from graia.saya import Channel
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast import ListenerSchema

from graia.ariadne.message.element import Image,Plain, Source, Quote, Voice
from graia.ariadne.model import Group

import asyncio
            
from .utils import gentoSSTV,genMORSvoice


sst = Channel.current()

sst.name("SSTV")
sst.author("道锋潜鳞")
sst.description("SSTV计算")


@sst.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(".sstv").help("主控制器"),
                    ArgumentMatch("-type",optional=True) @ "mod"
                ]
            )
        ],
    )
)
async def ai_handle(
    app: Ariadne,
    group: Group,
    message: MessageChain,
    mod: MatchResult
):
    
    if not message.has(Quote):
        await app.send_group_message(
            target=group,
            message=MessageChain(
                Plain("调用失败，您必须指定回复一条包含图像的消息")
            ),
            quote=message.get_first(Source)

        )
        return
    source = message.get_first(Quote)
    try:
        quote = await app.get_message_from_id(source.id)
    except:
        await app.send_group_message(
            target=group,
            message=MessageChain(
                Plain("啊哦，找不到你回复的消息了")
            ),
            quote=message.get_first(Source)

        )
        return
    if not quote.message_chain.has(Image):
        await app.send_group_message(
            target=group,
            message=MessageChain(
                Plain("调用失败，您必须指定回复一条包含图像的消息")
            ),
            quote=message.get_first(Source)

        )
        return
    
    if len(quote.message_chain.get(Image)) > 1:
        await app.send_group_message(
            target=group,
            message=MessageChain(
                Plain("调用失败，图像只能为一张")
            ),
            quote=message.get_first(Source)

        )
        return
    
    image:Image = quote.message_chain.get_first(Image)
    
    try:
        voice = await asyncio.create_task(
            gentoSSTV(mod=mod,imgdata=await image.get_bytes())
        )
        await app.send_group_message(
            target=group,
            message=MessageChain(
                Voice(data_bytes=voice)
            )
        )
    except Exception:
        await app.send_group_message(
            target=group,
            message=MessageChain(
                "生成错误"
            )
        )


@sst.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(".mors").help("主控制器"),
                    ArgumentMatch("-cM",optional=True) @ "codeMulti",
                    ArgumentMatch("-sM",optional=True) @ "splitMulti",
                    WildcardMatch() @ "text"
                ]
            )
        ],
    )
)
async def ai_handle(
    app: Ariadne,
    group: Group,
    text:MatchResult,
    codeMulti:MatchResult,
    splitMulti:MatchResult
):  
    if codeMulti.matched:
        codeMulti = int(codeMulti.result.display)
    else:
        codeMulti = 0

    if splitMulti.matched:
        splitMulti = int(splitMulti.result.display)
    else:
        splitMulti = 1


    text = text.result.display
    if not text:
        await app.send_group_message(
            target=group,
            message=MessageChain(
                "生成错误,转换内容为空"
            )
        )
        return

    if len(text) > 100:
        await app.send_group_message(
            target=group,
            message=MessageChain(
                "你的文章太长啦，神鳞不想被tx口球XWX"
            )
        )
        return

    try:
        voice = await genMORSvoice(text,codeMulti,splitMulti)
        await app.send_group_message(
                target=group,
                message=MessageChain(
                    Voice(data_bytes=voice)
                )
            )
    except Exception:
        await app.send_group_message(
            target=group,
            message=MessageChain(
                "生成错误"
            )
        )