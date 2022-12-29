from graia.ariadne.app import Ariadne
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    ArgumentMatch
)
from graia.saya import Channel
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast import ListenerSchema

from graia.ariadne.message.element import Image,Plain, Source, Quote, Voice
from graia.ariadne.model import Group
from graiax import silkcoder

import asyncio

from pysstv.color import (
    MartinM1,
    MartinM2,
    Robot36,
    ScottieS1,
    ScottieS2
)
import PIL.Image as PIMG
from io import BytesIO
from aiocache import cached


from threading import Thread
class MyThread(Thread):
    def __init__(self, func, args):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            self.result = self.func(*self.args)
        except Exception:
            return None

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None
            



@cached(ttl=30000)
async def gentoSSTV(mod: MatchResult,imgdata):
    if mod.matched:
        mod = mod.result.display
    else:
        mod = "M1"
    ret = BytesIO()
    img = PIMG.open(
        BytesIO(
                imgdata
            )).convert("RGB")

    img = img.resize((320,int((320/img.width)*img.height)))
    if mod == "M1":
        a = MartinM1(image=img,samples_per_sec=48000,bits=16)
    elif mod == "M2":
        a = MartinM2(image=img,samples_per_sec=48000,bits=16)
    elif mod == "R36":
        a = Robot36(image=img,samples_per_sec=48000,bits=16)
    elif mod == "S1":
        a = ScottieS1(image=img,samples_per_sec=48000,bits=16)
    elif mod == "S2":
        a = ScottieS2(image=img,samples_per_sec=48000,bits=16)
    else:
        a = MartinM1(image=img,samples_per_sec=48000,bits=16)

    t1 = MyThread(a.write_wav, args=(ret,))
    t1.start()
    while t1.is_alive():
        await asyncio.sleep(1)
    ret.seek(0)
    audio_bytes = await silkcoder.async_encode(ret.read(), ios_adaptive=True)
    return audio_bytes


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
    except:
        await app.send_group_message(
            target=group,
            message=MessageChain(
                "生成错误"
            )
        )