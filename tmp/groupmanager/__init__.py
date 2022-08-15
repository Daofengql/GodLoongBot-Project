from library.config import config
from library.depend import Permission, FunctionCall
from library.model import UserPerm
import pickle
from graia.ariadne import Ariadne
import asyncio
import os
from graia.ariadne.event.mirai import BotInvitedJoinGroupRequestEvent,NewFriendRequestEvent,MemberJoinEvent,MemberLeaveEventQuit,MemberLeaveEventKick,MemberMuteEvent
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.broadcast.interrupt import Waiter, InterruptControl
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    WildcardMatch,
    RegexMatch
)
import re,random
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
import random
from datetime import datetime
from graia.ariadne.message.element import At, Image, Forward, ForwardNode
from graia.ariadne.model import Group

pattern = re.compile(r'[\u4e00-\u9fa5A-Za-z0-9^=?$\x22.]+')
PATH = os.path.dirname(__file__)+"/cache/" 
g = Channel.current()

g.name("管理员群管理插件")
g.author("道锋潜鳞")
g.description("管理账号群数据")

async def allgroup(app,group):
        
    grouplist = await app.get_group_list()
    member_list = await app.get_member_list(group)
    fwd_nodeList = [
        ForwardNode(
                target=random.choice(member_list),
                time=datetime.now(),
                name = f"{random.choice(member_list).name}",
                message=MessageChain(f"一共{len(grouplist)}个群聊")
            )
        ]
    count = 0
    reply = ""
    for groups in grouplist:
        try:name = str(pattern.search(groups.name.strip()).group())
        except:name = ""
        reply = reply +f"群号:{groups.id}  群名:{name}  机器人权限:{str(groups.account_perm)}\n"
        count +=1
        if count %6 == 1 or count==len(grouplist):
            fwd_nodeList.append(
                ForwardNode(
                    target=random.choice(member_list),
                    name = f"{random.choice(member_list).name}",
                    time=datetime.now(),
                    message=MessageChain(reply)
                )
            )
            reply = "" 
    return MessageChain([Forward(fwd_nodeList)])

async def alluser(app):
    
    grouplist = await app.get_group_list()
    userlist=[]
    adminlist=[]
    for groups in grouplist:
        if not str(groups.account_perm) == "MEMBER":adminlist.append(groups.id)
        member_list = await app.get_member_list(groups.id)
        for member in member_list:
            if member.id not in userlist:userlist.append(member.id)
    
    return MessageChain(f"当前服务群聊：{len(grouplist)}  覆盖人数：{len(userlist)}(已去重)  在{len(adminlist)}个群中具有管理员或更高权限")


@g.use(ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(".group","群聊").help('群聊控制'),
                    UnionMatch(
                        "leave",
                        "list",
                        "covered",
                        "广播","broadcast"
                    )@ "func",
                    WildcardMatch() @ "param",
                ]
            )
        ],
        decorators=[
            Permission.require(
                UserPerm.BOT_OWNER, MessageChain("权限不足，你需要来自 所有人 的权限才能进行本操作")
            ),
            FunctionCall.record(g.module),
        ],
    )
)
async def groupfunc(app: Ariadne,
    event:GroupMessage,
    group: Group, 
    func: MatchResult, 
    param: MatchResult):
        
    func = func.result.display
    msg = None
    if func == "list": msg = await allgroup(app,group)
    elif func == "covered":msg = await alluser(app)
    elif func == "leave":
        try:int(param.result.display)
        except:msg = MessageChain(f"退出失败")
        else:
            await app.quit_group(int(param.result.display))
            msg = MessageChain(f"已退出群聊：{param.result.display}")
        return
    elif func in ("广播","broadcast"):
        await app.send_message(group, MessageChain("请发送你要广播的内容，exit退出~"))
        
        @Waiter.create_using_function(listening_events=[GroupMessage])
        async def waiter(waiter_message: MessageChain, g: Group, e: GroupMessage):
            if e.sender.id == event.sender.id and g.id == group.id:
                saying = waiter_message.display
                if saying == "exit":
                    await app.send_message(group, MessageChain("广播已暂停"))
                    return False,None
                elif saying:return True,e
                else:return False,None
            
        try:
            status, dat = await asyncio.wait_for(
                InterruptControl(app.broadcast).wait(waiter), 600
            )
        except asyncio.exceptions.TimeoutError:
            await app.send_message(group, MessageChain("超时拉~"))
            return
        if status:
            if param.result.display:grouplist = [int(x) for x in param.result.display.split() if x.isdigit()]
            else: grouplist = await app.get_group_list()
            for gs in grouplist:
                await asyncio.sleep(random.randint(1,10))
                try:await app.send_group_message(gs, dat.message_chain)
                except:pass
            await app.send_message(group, MessageChain("广播完成了~"))
            return
    
    
    if msg:
        await app.send_message(
            event.sender.group if isinstance(event, GroupMessage) else event.sender, msg
        )
 
 
 
 
       
#拉群邀请 
@g.use(ListenerSchema(listening_events=[BotInvitedJoinGroupRequestEvent]))
async def BIJGRE(app: Ariadne, event: BotInvitedJoinGroupRequestEvent):
    if event.supplicant == config.owners[0]:
        await event.accept()
        return
    
    await app.send_friend_message(
            event.supplicant,
            f"您的申请已经上呈给龙帝进行抉择了，请您等待一段时间~~~"
        )
        
    reqId = event.request_id
    await app.send_friend_message(
        config.owners[0],
        f"{event.nickname}({event.supplicant}) 邀请机器人加入 {event.group_name}({event.source_group})\n同意：\n同意加群 {reqId}\n不同：\n不同意加群 {reqId}"
        )
    pickle.dump(event,open(PATH+f"group_{reqId}.pkl", 'wb'))


@g.use(ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("同意加群","不同意加群")@ "func",
                    RegexMatch(r"\d+") @ "param",
                ]
            )
        ],
        decorators=[
            Permission.require(
                UserPerm.BOT_OWNER, MessageChain("权限不足，你需要来自 所有人 的权限才能进行本操作")
            ),
            FunctionCall.record(g.module),
        ],
    )
)    
async def BIJGRE_Handle(app: Ariadne, event: FriendMessage,param: MatchResult,func:MatchResult):
    func = func.result.display
    param = param.result.display
    if not os.path.exists(PATH+f"group_{param}.pkl"):
        await app.send_friend_message(
            config.owners[0],
            f"操作失败，没有这个请求，请检查参数是否错误"
        )
        return
    
    event = pickle.load(open(PATH+f"group_{param}.pkl", 'rb'))
    if func =="同意加群":
        await app.send_friend_message(
            event.supplicant,
            f"您的申请龙帝已经通过了~！！"
        )
        await event.accept()
        await app.send_friend_message(
            config.owners[0],
            f"加入成功"
        )

    elif func =="不同意加群":
        await app.send_friend_message(
            event.supplicant,
            f"很抱歉，您的申请龙帝没有批准~~~"
        )
        await event.reject()
        await app.send_friend_message(
            config.owners[0],
            f"已拒绝加入"
        )

    else:pass
    os.remove(PATH+f"group_{param}.pkl")






#好友申请
@g.use(ListenerSchema(listening_events=[NewFriendRequestEvent ]))
async def NFRE(app: Ariadne, event: NewFriendRequestEvent):
       
    reqId = event.request_id
    await app.send_friend_message(
        config.owners[0],
        f"{event.nickname}({event.supplicant}) 申请添加机器人为好友 申请消息：{event.message}\n同意：\n同意好友 {reqId}\n不同意：\n不同意好友 {reqId}"
        )
    pickle.dump(event,open(PATH+f"friend_{reqId}.pkl", 'wb'))


@g.use(ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("同意好友","不同意好友")@ "func",
                    RegexMatch(r"\d+") @ "param",
                ]
            )
        ],
        decorators=[
            Permission.require(
                UserPerm.BOT_OWNER, MessageChain("权限不足，你需要来自 所有人 的权限才能进行本操作")
            ),
            FunctionCall.record(g.module),
        ],
    )
)    
async def NFRE_Handle(app: Ariadne, event: FriendMessage,param: MatchResult,func:MatchResult):
    func = func.result.display
    param = param.result.display
    
    if not os.path.exists(PATH+f"friend_{param}.pkl"):
        await app.send_friend_message(
            config.owners[0],
            f"操作失败，没有这个请求，请检查参数是否错误"
        )
        return
    
    event = pickle.load(open(PATH+f"friend_{param}.pkl", 'rb'))
    
    if func =="同意好友":
        await event.accept()
        await app.send_friend_message(
            config.owners[0],
            f"加入成功"
        )

    elif func =="不同意好友":
        await event.reject()
        await app.send_friend_message(
            config.owners[0],
            f"已拒绝加入"
        )

    else:pass
    os.remove(PATH+f"friend_{param}.pkl")
    
    
#加群欢迎
@g.use(ListenerSchema(listening_events=[MemberJoinEvent]))
async def MJE(app: Ariadne, event: MemberJoinEvent):
    await app.send_group_message(
        event.member.group,
        MessageChain(
            Image(data_bytes = await event.member.get_avatar()),
            At(event.member.id),
            "欢迎加入本群哦"
            )
        )
        
#主动退群
@g.use(ListenerSchema(listening_events=[MemberLeaveEventQuit]))
async def MLEQ(app: Ariadne, event: MemberLeaveEventQuit):
    await app.send_group_message(
        event.member.group,
        MessageChain(
            f"{event.member.id}好像退出了本群哦，发生什么事了吗？"
            )
        )
        
#被踢出群聊
@g.use(ListenerSchema(listening_events=[MemberLeaveEventKick]))
async def MLEK(app: Ariadne, event: MemberLeaveEventKick):
    await app.send_group_message(
        event.member.group,
        MessageChain(
            f"{event.member.id}好像犯了什么事哦，被管理员/群主踢出去了~ 大家引以为戒"
            )
        )


#被禁言
@g.use(ListenerSchema(listening_events=[MemberMuteEvent]))
async def MME(app: Ariadne, event: MemberMuteEvent):
    if event.member.id == config.account:return
    await app.send_group_message(
        event.member.group,
        MessageChain(
            f"{event.member.id}被禁言了{event.duration}秒哦，大家要谨言慎行"
            )
        )
        
#被解除禁言
@g.use(ListenerSchema(listening_events=[MemberMuteEvent]))
async def MME(app: Ariadne, event: MemberMuteEvent):
    if event.member.id == config.account:
        await app.send_group_message(
            event.member.group,
            MessageChain(
                f"啊哈哈哈，我又回来了（管理员高抬贵手~）"
                )
            )
        return
    await app.send_group_message(
        event.member.group,
        MessageChain(
            f"{event.member.id}被禁言了{event.duration}秒哦，大家要谨言慎行"
            )
        )
        