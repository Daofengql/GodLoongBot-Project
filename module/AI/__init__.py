import asyncio
from io import BytesIO

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import GroupRecallEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain, Quote, Source, Voice
from graia.ariadne.message.parser.twilight import (ArgumentMatch, MatchResult,
                                                   Twilight, UnionMatch,
                                                   WildcardMatch)
from graia.ariadne.model import Group
from graia.broadcast.interrupt import InterruptControl, Waiter
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graiax import silkcoder



from library.ComputerVisual import ApiConfig, ComputerVisual, Speech, Translate
from library.image.oneui_mock.elements import *

from pydub import AudioSegment
from pydub.effects import high_pass_filter,normalize
import copy
import io


#机械音效果控制器
def add_mechanical_effect(input_audio_bytesio):
    # 从BytesIO对象中读取WAV音频数据
    input_audio_bytesio.seek(0)
    audio = AudioSegment.from_file(input_audio_bytesio, format='wav')

    # 添加机械音效（低通滤波器）
    modified_audio = high_pass_filter(audio, cutoff=1500)

    amplified_audio = normalize(modified_audio)

    #进行深度复制
    mix_audio1 = copy.deepcopy(amplified_audio)
    mix_audio2 = copy.deepcopy(amplified_audio)
    
    #设置漂移延迟
    time_offset_ms = 3

    #将音量减半
    mix_audio1 = mix_audio1 - 6  # 以分贝为单位进行音量调整
    mix_audio2 = mix_audio2 - 6

    # 计算时间偏移的帧数
    time_offset_frames = int(time_offset_ms * mix_audio1.frame_rate / 1000)

    # 将第二段音频向后偏移指定的帧数
    mix_audio2 = mix_audio2.overlay(mix_audio2, position=time_offset_frames)

    # 将两段音频叠加在一起
    mixed_audio = mix_audio1.overlay(mix_audio2)

    # 保存叠加后的音频到BytesIO对象
    output_audio = io.BytesIO()
    mixed_audio.export(output_audio, format='wav')

    # 将BytesIO对象中的音频数据读取为bytes
    output_audio_bytes = output_audio.getvalue()

    return output_audio_bytes



ai = Channel.current()

ai.name("AI计算")
ai.author("道锋潜鳞")
ai.description("AI计算")



conf = ApiConfig(Subscription="",region="eastasia")
speech = Speech(Subscription="",region="eastasia")
trans = Translate(Subscription="",region="eastasia")
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
    func: MatchResult,
    source: Source
):
    func = func.result.display
    
    if not message.has(Quote):
        await app.send_group_message(
            target=group,
            message=MessageChain(
                Plain("调用失败，您必须指定回复一条包含图像的消息")
            ),
            quote=source

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
            quote=source

        )
        return
    if not quote.message_chain.has(Image):
        await app.send_group_message(
            target=group,
            message=MessageChain(
                Plain("调用失败，您必须指定回复一条包含图像的消息")
            ),
            quote=source

        )
        return
    
    if len(quote.message_chain.get(Image)) > 1:
        await app.send_group_message(
            target=group,
            message=MessageChain(
                Plain("调用失败，图像只能为一张")
            ),
            quote=source

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

        tmp = ", ".join([tag.name for tag in AZresult.tags])

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
            quote=source

        )
    return



@ai.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(".aztts").help("主控制器"),
                    ArgumentMatch("-style",optional=True) @ "style",
                    ArgumentMatch("-lang",optional=True) @ "lang",
                    ArgumentMatch("-speed",optional=True) @ "speed",
                    ArgumentMatch("-pitch",optional=True) @ "pitch",
                    WildcardMatch() @ "param"
                ]
            )
        ],
    )
)
async def speak_handle(
    app: Ariadne,
    group: Group,
    message: MessageChain,
    param: MatchResult,
    style: MatchResult,
    lang: MatchResult,
    speed: MatchResult,
    pitch: MatchResult,
    source: Source
):
    param = param.result.display
    if style.matched:
        style = style.result.display
    else:
        style = "customerservice"
        
    if style not in speech.STYLELIST:
        await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain("调用失败，您输入的语音风格不存在，暂时无法使用")
                )

            )
        return



    if lang.matched:
        lang = lang.result.display
    else:
        lang = "zh-CN-YunyangNeural"

    if lang not in speech.LANGLIST:
        await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain("调用失败，您输入的语音原型不存在，暂时无法使用")
                )

            )
        return
    elif style not in speech.LANGLIST[lang]:
        await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain("调用失败，您输入的语音风格暂不支持当前语音模型")
                )

            )
        return



    if speed.matched:
        try:
            speed = int(speed.result.display)
        except:
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain("调用失败，您输入的速度不是百分数（不需要百分号）")
                )

            )
            return

    else:
        speed = -15


    if pitch.matched:
        try:
            pitch = int(pitch.result.display)
        except:
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain("调用失败，您输入的语调变化不是百分数（不需要百分号）")
                )

            )
            return

    else:
        pitch = -7 

    if not param:
        if not message.has(Quote):
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain("调用失败，您必须指定回复一条包含文字的消息，或携带需要转换内容")
                ),
                quote=source

            )
            return
            
        source = message.get_first(Quote)

        quote = await app.get_message_from_id(source.id)
        if not quote.message_chain.has(Plain):
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain("调用失败，您必须指定回复一条包含文字的消息，或携带需要转换内容")
                ),
                quote=source

            )
            return
        param = ""
        for t in quote.message_chain.get(Plain):
            param = param + t.text
            
    if len(param) > 200:
        param = param[0:200]  + "。<break time='100ms' />哎呀太长了，神麟罢工了"

    getAPIdata = await speech.genAudioVoice(voice_name=lang,context=param,style=style,speed=speed,pitch=pitch)
    APIdata=BytesIO(getAPIdata)
    effect = add_mechanical_effect(APIdata)
    audio_bytes = await silkcoder.async_encode(effect, ios_adaptive=True)
    await app.send_group_message(
        target=group,
        message=MessageChain(
            Voice(data_bytes=audio_bytes)
        )
    )


BGMS = [
    "https://objectstorage.global.loongapi.com/loongapiSources/media/bot/aitts/Time_Back.wav",
    "https://objectstorage.global.loongapi.com/loongapiSources/media/bot/aitts/The_Hotest_Music.mp3",
    "https://objectstorage.global.loongapi.com/loongapiSources/media/bot/aitts/Trip.wav",
    "https://objectstorage.global.loongapi.com/loongapiSources/media/bot/aitts/pddHHZL.wav",
    "https://objectstorage.global.loongapi.com/loongapiSources/media/bot/aitts/My_Soul.wav",
    "https://objectstorage.global.loongapi.com/loongapiSources/media/bot/aitts/The_Right_Path.wav",
    "https://objectstorage.global.loongapi.com/loongapiSources/media/bot/aitts/Paris.wav"
]

@ai.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("营销号生成","小帅").help("主控制器"),
                    ArgumentMatch("-bgm",optional=True) @ "bgm",
                    WildcardMatch() @ "param"
                ]
            )
        ],
    )
)
async def VideoYingxiaohao_handle(
    app: Ariadne,
    group: Group,
    message: MessageChain,
    param: MatchResult,
    bgm: MatchResult,
    source: Source
):
    param = param.result.display
    style = "cheerful"
    lang = "zh-CN-YunxiNeural"
    speed = 0
    pitch = 0

    bg = {"volume":0.5,"url":""}
    
    if not param:
        if not message.has(Quote):
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain("调用失败，您必须指定回复一条包含文字的消息，或携带需要转换内容")
                ),
                quote=source

            )
            return
            
        source = message.get_first(Quote)

        quote = await app.get_message_from_id(source.id)
        if not quote.message_chain.has(Plain):
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain("调用失败，您必须指定回复一条包含文字的消息，或携带需要转换内容")
                ),
                quote=source

            )
            return
        param = ""
        for t in quote.message_chain.get(Plain):
            param = param + t.text

    if bgm.matched:
        try:
            bgm = int(bgm.result.display)
        except:
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain("调用失败，您输入的bgm不是数字")
                )

            )
            return
        bg["url"] = BGMS[bgm]
    else:
        bg["url"] = random.choice(BGMS)
    

    getAPIdata = await speech.genAudioVoice(voice_name=lang,context=param,style=style,speed=speed,pitch=pitch,bg=bg)
    audio_bytes = await silkcoder.async_encode(getAPIdata, ios_adaptive=True)
    await app.send_group_message(
        target=group,
        message=MessageChain(
            Voice(data_bytes=audio_bytes)
        )
    )
    

@ai.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(".aztranslate","翻译").help("主控制器"),
                    ArgumentMatch("-origin",optional=True) @ "origin",
                    ArgumentMatch("-target",optional=True) @ "target",
                    WildcardMatch() @ "param"
                ]
            )
        ],
    )
)
async def translate_handle(
    app: Ariadne,
    group: Group,
    message: MessageChain,
    origin: MatchResult,
    target: MatchResult,
    param: MatchResult,
    source: Source
    
):
    param = param.result.display
    
    if not param:
        if not message.has(Quote):
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain("调用失败，您必须指定回复一条包含文字的消息，或携带需要转换内容")
                ),
                quote=source

            )
            return
            
        source = message.get_first(Quote)

        quote = await app.get_message_from_id(source.id)
        if not quote.message_chain.has(Plain):
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain("调用失败，您必须指定回复一条包含文字的消息，或携带需要转换内容")
                ),
                quote=source

            )
            return
        param = ""
        for t in quote.message_chain.get(Plain):
            param = param + t.text

    if target.matched:
        target = target.result.display
    else:
        target = "en"

    if origin.matched:
        origin = origin.result.display
    else:
        origin = ""
    if origin:
        if not (origin in trans.Langs and target in trans.Langs):
            await app.send_group_message(
                    target=group,
                    message=MessageChain(
                        Plain("调用失败，您的目标语言和源语言不合法")
                    ),
                    quote=source

                )
            return

    ret = await trans.Translate(text=param,orgin=origin,target=target)
    if not ret:
        ret = "啊哦，翻译出错了"

    await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain(ret)
                ),
                quote=source

    )
