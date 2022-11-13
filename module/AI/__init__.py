from graia.ariadne.app import Ariadne
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    WildcardMatch,
)

from graia.saya import Channel
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast import ListenerSchema
from library.image.oneui_mock.elements import *
from graia.ariadne.message.element import Image,Plain, Source,Quote
from graia.ariadne.model import Group

from library.ComputerVisual import ComputerVisual,ApiConfig

ai = Channel.current()

ai.name("AI计算")
ai.author("道锋潜鳞")
ai.description("AI计算")


conf = ApiConfig(Subscription="400c559601f943e6ba37932cfbcfa6b4",region="eastasia")
azCV = ComputerVisual.ComputerVisual(config=conf)

@ai.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(".ai").help("主控制器"),
                    UnionMatch(
                        "介绍一下","-describe",
                        "打个标签","-tags",
                        ) @ "func"
                ]
            )
        ],
    )
)
async def ai_handle(
    app: Ariadne,
    group: Group,
    event: GroupMessage,
    message: MessageChain,
    func: MatchResult
):
    func = func.result.display
    
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

    quote = await app.get_message_from_id(source.id)
    
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
    if func in ("介绍一下","-describe"):

        AZresult = await azCV.DescribeImage(ImageURL=image.url,maxCandidates=5)
        if len(AZresult.description.captions)>1:
            back = Plain(f"\n另外神麟觉得这张图的内容也有可能是：{AZresult.description.captions[1].text}\n这种可能有：{round(AZresult.description.captions[1].confidence*100,3)}% 的可能性\n")
        else:
            back = Plain("")
        mes = MessageChain(
            Plain("神麟分析了您的图片\n"),
            Plain(f"神麟认为，这张图的内容有可能是：{AZresult.description.captions[0].text}\n"),
            Plain(f"这个结果神麟觉得有：{round(AZresult.description.captions[0].confidence*100,3)}% 的可能性"),
            back

        )

    elif func in ("打个标签","-tags"):

        AZresult = await azCV.TagImage(ImageURL=image.url)
        tmp = ""
        for tag in AZresult.tags:
            tmp = tmp + tag.name + ", "
        mes = MessageChain(
            Plain("神麟分析了您的图片\n"),
            Plain(f"神麟为您给出了如下，关于此图在神麟眼中可能的标签：\n"),
            Plain(tmp[:-2])
        )
    else:
        mes = MessageChain(
            Plain("啊哦，神鳞不会哦，以后在学习"),
        )



    await app.send_group_message(
            target=group,
            message=mes,
            quote=message.get_first(Source)

        )
    return

    