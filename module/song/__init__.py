import asyncio
import datetime
from library.config import config
from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    WildcardMatch,
    ArgumentMatch
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
                    ArgumentMatch("-func", optional=True ) @ "func",
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
    
    if func.matched:
        func = func.result.display
    else:
        func = "网易"

    name = param.result.display

    if func == "帮助":
        await app.send_message(
            group,
            MessageChain(
                "使用方可以访问具体使用说明文档",
                config.docs + "help/ent/music/",
                "来获取更加详细的使用方法"
                )
            )
        return

    elif func == "网易" and name:  f = "netease"
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
        dat = await eval(f"song.{f}")(l, dat)
        try:
            await app.send_message(
                group,
                MessageChain(
                    dat
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