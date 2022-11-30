import asyncio
import datetime
from library.config import config
from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import MusicShare
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    WildcardMatch,
)
from graia.ariadne.model import Group
from graia.broadcast.interrupt import Waiter, InterruptControl
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from . import song

reply = Channel.current()

reply.name("点歌")
reply.author("道锋潜鳞")
reply.description("点歌控制器")

LAST_REQUEST = datetime.datetime.now()

SONGED = []

async def limit_check():
    global LAST_REQUEST
    now_time = datetime.datetime.now()
    if (now_time - LAST_REQUEST) > datetime.timedelta(seconds=3):
        LAST_REQUEST = datetime.datetime.now()
        return True
    return False

@reply.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(".song", "点歌").help("点歌控制器"),
                    UnionMatch(
                        "-网易","-netease",
                        "-酷狗", "-kugo",
                        "-帮助","-help"
                        
                    )
                    @ "func",
                    WildcardMatch() @ "param",
                ]
            )
        ],
    )
)
async def diange(
    app: Ariadne,
    group: Group,
    event: GroupMessage,
    func: MatchResult,
    param: MatchResult,
):
    if not await limit_check():
        await app.send_message(group, MessageChain("嗷呜~ 太快了"))
        return
    
    global SONGED
    if event.sender.id in SONGED:
        await app.send_message(group, MessageChain("嗷呜~ 你已经有一个正在点歌的任务"))
        return
    
    func = func.result.display
    name = param.result.display
    if func in ("-网易", "-netease") and name:  f = "netease"
    elif func in ("-酷狗", "-kugo") and name:  f = "kugomusic"
    elif func in ("-帮助","-help"):
        await app.send_message(
            group,
            MessageChain(
                "使用方法如下：\n\n",
                "使用网易数据源：\n",
                "点歌 -网易 [歌曲名]\n",
                "点歌 -netease [歌曲名]\n\n",
                "使用酷狗数据源：\n",
                "点歌 -酷狗 [歌曲名]\n",
                "点歌 -kugou [歌曲名]\n\n",
                "您也可以访问具体使用说明文档",
                config.docs + "help/ent/music/",
                "来获取更加详细的使用方法"
                )
            )
        return
        
    else: return
        
    l = await eval(f"song.get_{f}")(name, app, group, event)
    
    
    
    SONGED.append(event.sender.id)
    
    @Waiter.create_using_function(listening_events=[GroupMessage])
    async def waiter(waiter_message: MessageChain, g: Group, e: GroupMessage):
        if e.sender.id == event.sender.id and g.id == group.id:
            saying = waiter_message.display
            try:
                if 0 <= int(saying) <= len(l):  return True, int(saying)
                else:  return False, 0
            except:return False, 0

    try:
        status, dat = await asyncio.wait_for(
            InterruptControl(app.broadcast).wait(waiter), 600
        )
    except asyncio.exceptions.TimeoutError:
        await app.send_message(group, MessageChain("超时拉~"))
        SONGED.remove(event.sender.id)
        return
    if status:
        dat = song.ObjectDict(await eval(f"song.{f}")(l, dat))
        try:
            await app.send_message(
                group,
                MessageChain(
                    MusicShare(
                        brief=dat.brief,
                        jumpUrl=dat.jumpUrl,
                        kind=dat.kind,
                        musicUrl=dat.musicUrl,
                        pictureUrl=dat.pictureUrl,
                        summary=dat.summary,
                        title=dat.title,
                    )
                ),
            )
        except: await app.send_message(group, MessageChain("点歌失败了，可能这是一个vip歌曲"))
        finally:
            SONGED.remove(event.sender.id)
            return
    else:
        await app.send_message(group, MessageChain("你发的东西好像有点问题哈~"))
        SONGED.remove(event.sender.id)
        return



@reply.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(".song", "点歌").help("点歌控制器"),
                    WildcardMatch() @ "param",
                ]
            )
        ],
    )
)
async def diangehelp(
    app: Ariadne,
    message: MessageChain,
    group: Group,
    event: GroupMessage,
    param: MatchResult
):
    if "-" in param.result.display: return
    await app.send_message(
        group, 
        MessageChain(
            "点歌的操作方法已经出现了变化\n",
            "您可以发送 点歌 -帮助 来获取使用帮助，不要忘记中间有一个空格哦\n",
            "您也可以访问具体使用说明文档",
            config.docs + "help/music",
            "来获取更加详细的使用方法"
            )
        )
    return