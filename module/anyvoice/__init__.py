from library.config import config
from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graiax import silkcoder
import random
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult
)
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.ariadne.message.element import Voice
from graia.ariadne.model import Group
import os
import datetime

reply = Channel.current()

reply.name("reply")
reply.author("道锋潜鳞")
reply.description("自动回复")

PATH = os.path.dirname(__file__)+"/voice/"

LAST_QEQUEST = datetime.datetime.now()
async def limit_check():
    global LAST_QEQUEST
    nowtime = datetime.datetime.now()
    if (nowtime-LAST_QEQUEST) > datetime.timedelta(seconds = 3):
        LAST_QEQUEST = datetime.datetime.now()
        return True
    return False
    

async def getvoice(func):
    audio_bytes = await silkcoder.async_encode(f"{PATH}{func}/{random.choice(os.listdir(PATH+func+'/'))}", ios_adaptive=True)
    return audio_bytes
        
@reply.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(".voice").help('音频控制器'),
                    UnionMatch(
                        "-Stellaris","-stellaris","-群星",
                        "-h","-帮助"
                        
                    )@ "func"
                ]
            )
        ]
        )
    )
async def hello(
    app: Ariadne, 
    group: Group,
    func: MatchResult
    ):
    if not await limit_check():
        await app.send_message(
        group,
        MessageChain("嗷呜~ 太快了")
        )
        return
    
    func = func.result.display
    if func in ("-Stellaris","-stellaris","-群星"):audio_bytes = await getvoice("Stellaris")
    elif func in ("-h","-帮助"):
        await app.send_message(
        group, 
        MessageChain(
            "欢迎使用来点语音功能哦\n",
            "您可以访问具体使用说明文档",
            config.docs + "help/anyvoice",
            "来获取更加详细的使用方法"
            )
        )
        return
    await app.send_message(
             group,
            MessageChain(Voice(data_bytes=audio_bytes))
         )
    