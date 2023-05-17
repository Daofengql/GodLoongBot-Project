import calendar
import datetime
from io import BytesIO

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain, Source
from graia.ariadne.message.parser.twilight import (ArgumentMatch, ElementMatch,
                                                   ElementResult, FullMatch,
                                                   MatchResult, RegexMatch,
                                                   RegexResult, Twilight,
                                                   UnionMatch, WildcardMatch)
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from lxml import etree
from PIL import Image as PLImg
from xpinyin import Pinyin

from library.Bot import bot

from .utils import WaitForResp, getBT, searchFromPage

BOT = bot()
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
        choice  = choice.display
        try:
            choice = int(choice)
        except:
            await app.send_group_message(
                target=group,
                message="回复好像不规范哦",
                quote=message.get_first(Source)
            )
            return

        if choice > len(pages):
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

@et.use(ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(".uegcard",".uegCard","。uegcard","联合政府通行证"),
                    WildcardMatch() @ "param"
                ]
            )
        ]
    )
)
async def uegmod(
    app: Ariadne,
    group: Group,
    event: GroupMessage,
    message: MessageChain,
    param: MatchResult
):
    session = Ariadne.service.client_session
    time = datetime.datetime.today()

    if param.matched and str(param.result.display).strip() == "-f":

        data = {
            "position" : None,
            "Firstname" : None,
            "Secondname" : None,
            "barcodeContent":str( event.sender.id).rjust(12,"0"),
            "qrcodeContent":None,
            "signTime":f"{time.day} {calendar.month_abbr[time.month]} {time.year}",
            "avatar":None,
        }
        await app.send_group_message(
            target=group,
            message=MessageChain(
                Plain(
                    "请回复您的姓氏，或作为大字号显示的名字，退出请回复exit"
                )
            ),
            quote=message.get_first(Source)
        )

        choice = await WaitForResp(app,group,event,message)
        if choice.display == "exit":
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain(
                        "已退出生成"
                    )
                ),
                quote=message.get_first(Source)
            )
            return
        data["Firstname"] = choice.display


        
        await app.send_group_message(
            target=group,
            message=MessageChain(
                Plain(
                    "请回复您的名字，或作为小字号显示的名字以及英文内容，退出请回复exit"
                )
            ),
            quote=message.get_first(Source)
        )
        choice = await WaitForResp(app,group,event,message)
        if choice.display == "exit":
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain(
                        "已退出生成"
                    )
                ),
                quote=message.get_first(Source)
            )
            return
        data["Secondname"] = choice.display


        await app.send_group_message(
            target=group,
            message=MessageChain(
                Plain(
                    "请回复您的职位，退出请回复exit"
                )
            ),
            quote=message.get_first(Source)
        )
        choice = await WaitForResp(app,group,event,message)
        if choice.display == "exit":
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain(
                        "已退出生成"
                    )
                ),
                quote=message.get_first(Source)
            )
            return
        data["position"] = choice.display

        
        await app.send_group_message(
            target=group,
            message=MessageChain(
                Plain(
                    "请回复您需要添加进二维码的内容，退出请回复exit"
                )
            ),
            quote=message.get_first(Source)
        )
        choice = await WaitForResp(app,group,event,message)
        if choice.display == "exit":
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain(
                        "已退出生成"
                    )
                ),
                quote=message.get_first(Source)
            )
            return
        data["qrcodeContent"] = choice.display

        
        await app.send_group_message(
            target=group,
            message=MessageChain(
                Plain(
                    "请回复您的照片，如果需要使用头像请随意回复文字，退出请回复exit"
                )
            ),
            quote=message.get_first(Source)
        )
        choice = await WaitForResp(app,group,event,message)
        if choice.display == "exit":
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    Plain(
                        "已退出生成"
                    )
                ),
                quote=message.get_first(Source)
            )
            return
        img = choice.get(Image)
        if not img:
            data["avatar"] = BytesIO(await event.sender.get_avatar())
        else:
            data["avatar"] = BytesIO(await img[0].get_bytes())

        print(data)

    else:
        member = await app.get_member(
            group=group,
            member_id=event.sender.id
        )
        s = Pinyin().get_pinyin(event.sender.name).split('-')
        result3 = s[0].capitalize() + ' ' + ''.join(s[1:]).capitalize()
        
        data = {
            "position" : str(member.permission),
            "Firstname" : event.sender.name,
            "Secondname" : result3,
            "barcodeContent":str( event.sender.id).rjust(12,"0"),
            "qrcodeContent":f"你好 {event.sender.name} 欢迎来到UEG",
            "signTime":f"{time.day} {calendar.month_abbr[time.month]} {time.year}",
            "avatar":BytesIO(await event.sender.get_avatar())
        }

    
    await app.send_group_message(
                target=group,
                message=MessageChain(
                    "正在为您生成身份信息卡....请耐心等待，若2分钟内无响应，您可以重新触发"
                )
            )
    async with session.post(f"https://v1.loongapi.com/v1/bot/MEMEs/WanderingEarth/UEG",data=data) as resp:
        if resp.status == 200:
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    Image(
                        data_bytes=await resp.read()
                    )
                )
            )

@et.use(ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(".流浪地球倒计时"),
                    ArgumentMatch("-Title",optional=False) @ "Title",
                    ArgumentMatch("-Time",optional=False) @ "Time",
                    ArgumentMatch("-TimeMethod",optional=False) @ "TimeMethod",
                    ArgumentMatch("-SecondLine",optional=False) @ "SecondLine",
                    ArgumentMatch("-LastLine",optional=False) @ "LastLine",
                    ArgumentMatch("-Fontcolor",optional=True) @ "Fontcolor",
                    ArgumentMatch("-Shadow",optional=True) @ "Shadow",
                    ArgumentMatch("-ShadowColor",optional=True) @ "ShadowColor",
                    ArgumentMatch("-ShadowWave",optional=True) @ "ShadowWave",
                    ArgumentMatch("-BGcolor",optional=True) @ "BGcolor",
                    ArgumentMatch("-gif",optional=True) @ "gif",
                    ArgumentMatch("-duration",optional=True) @ "duration",

                ]
            )
        ]
    )
)
async def uegmod(
    app: Ariadne,
    group: Group,
    event: GroupMessage,
    Title:MatchResult,
    Time:MatchResult,
    TimeMethod:MatchResult,
    SecondLine:MatchResult,
    LastLine:MatchResult,
    Fontcolor:MatchResult,
    Shadow:MatchResult,
    ShadowColor:MatchResult,
    ShadowWave:MatchResult,
    BGcolor: MatchResult,
    gif:MatchResult,
    duration:MatchResult,

):
    session = Ariadne.service.client_session
    
    data = {
        "Title" : Title.result.display,
        "Time" : int(Time.result.display),
        "TimeP" : TimeMethod.result.display,
        "SecondLine":str(SecondLine.result.display).replace("_"," "),
        "LastLine":str(LastLine.result.display).replace("_"," ")
    }

    if Fontcolor.matched:
        data["Fontcolor"] = Fontcolor.result.display

    if Shadow.matched:
        data["Shadow"] = bool(Shadow.result.display)
        
    if ShadowColor.matched:
        data["ShadowColor"] = ShadowColor.result.display

    if gif.matched:
        data["isgif"] = gif.result.display

    if BGcolor.matched:
        data["BGcolor"] = BGcolor.result.display

    if duration.matched:
        data["GifDuration"] = duration.result.display
    
    if ShadowWave.matched:
        if str(ShadowWave.result.display).isdigit():
            data["ShadowWave"] = int(ShadowWave.result.display)


    for i in BOT.weijingci:
        if i in str(data):
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    "内容存在违禁词，请遵纪守法谢谢"
                )
            )
            return

    await app.send_group_message(
                target=group,
                message=MessageChain(
                    "正在为您生成梗图....请耐心等待，若2分钟内无响应，您可以重新触发"
                )
            )
            
    async with session.post("https://v1.loongapi.com/v1/bot/MEMEs/WanderingEarth/logo",data=data) as resp:
        if resp.status == 200:

            await app.send_group_message(
                target=group,
                message=MessageChain(
                    Image(
                        data_bytes = await resp.read()
                    )
                )
            )
        else:
            await app.send_group_message(
                target=group,
                message=MessageChain(
                    "接口请求错误"
                )
            )

@et.use(ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(".幻影坦克"),
                    FullMatch("彩色", optional=True) @ "colorful",
                    RegexMatch(r"[\s]?", optional=True),
                    ElementMatch(Image) @ "img1",
                    RegexMatch(r"[\s]?", optional=True),
                    ElementMatch(Image) @ "img2",

                ]
            )
        ]
    )
)

async def ettank(
    app: Ariadne,
    message: MessageChain,
    group: Group,
    event: GroupMessage,
    source: Source,
    colorful: RegexResult,
    img1: ElementResult,
    img2: ElementResult,
): 
    img1: Image = img1.result
    img2: Image = img2.result
    display_img = BytesIO(await img1.get_bytes())
    hide_img = BytesIO(await img2.get_bytes())
    await app.send_group_message(
            target=group,
            message=MessageChain(
                "正在制作"
            ),
            quote=source
        )
    data = {
        "bimg":hide_img,
        "wimg":display_img
    }
    if colorful.matched:
        data["isColor"] = "true"

    session = Ariadne.service.client_session
    async with session.post("https://v1.loongapi.com/v1/bot/MEMEs/PhaTank",data=data) as resp:
        if resp.status  == 200:
            msg = Image(
                data_bytes=  await resp.read()
            )
        await app.send_group_message(
                target=group,
                message=msg,
                quote=source
            )


"""
@et.use(ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch(r"[a-zA-z]+://twitter.com/\w+/status/[0-9]+(.*)") @ "url"
                ]
            )
        ]
    )
)

async def ettank(
    app: Ariadne,
    message: MessageChain,
    group: Group,
    event: GroupMessage,
    source: Source,
    url: RegexResult,
):  

    session = Ariadne.service.client_session
    data = {
        "url":url.result.display,
        "ifRAW":True
    }
    async with session.post("https://v1.loongapi.com/v1/tool/playwright/firefox",data=data) as resp:
        if resp.status == 200:
            pagedata = (await resp.json())["result"]
        else:
            print(resp.status)
    
    
    html = etree.HTML(pagedata)
    html_data:list[etree._Element] = html.xpath('/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/div/article/div/div/div/div[3]/div[3]')
    for d  in html_data:
        print(d.text)
        
    """