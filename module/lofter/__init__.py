from library.config import config
from library.depend import Permission, FunctionCall
from library.model import UserPerm
from graia.ariadne import Ariadne
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
import random
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    ArgumentMatch,
    ArgResult,
    WildcardMatch,
    RegexMatch,
    ParamMatch,
)
import re,httpx,json
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast import ListenerSchema
import random
from datetime import datetime, timedelta
from graia.ariadne.message.element import At, Plain, Image, Forward, ForwardNode
from graia.ariadne.model import Group
from library.Bot import bot
BOT = bot()
pattern = re.compile(r'[\u4e00-\u9fa5A-Za-z0-9^=?$\x22.]+')


lofter = Channel.current()

lofter.name("lofter")
lofter.author("道锋潜鳞")
lofter.description("lofter随机图片 搜图")


class ObjectDict(object):
    def __init__(self, d):
        self.__d__ = d

    def __setattr__(self, key, value):
        if key == '__d__':
            return super.__setattr__(self, key, value)

        self.__d__.__setitem__(key, value)

    def __getattr__(self, item):
        if item == '__d__':
            return super.__getattr__(self, item)

        val = self.__d__.__getitem__(item)
        if isinstance(val, dict):
            return self.__class__(val)
        elif isinstance(val, list):
            return [self.__class__(d) for d in val]
        else:
            return val
            

async def getdata(func:str,args):
    ROOT_URL = "https://api.lofter.com/"
    url = ROOT_URL + func
    for i in BOT.weijingci:
        for k in args:
            if i in str(args[k]):return (3,"搜索暂停，您的参数含有违禁词","")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=args,timeout=120)
            if response.status_code != 200:  return (1,None,"")
            return (0,ObjectDict(json.loads(response.text)),json.loads(response.text))
    except: return (1,"获取数据错误","")
    
async def filter_tags(htmlstr):
    return str(pattern.search(htmlstr.strip()).group())

    
    
async def getHighHeatRandomPic(event,**args):
    if not args:func = "recommend/exploreRecom.json"
    else:func = "recommend/tagRecom.json"
    code,data,raw = await getdata(func,args)
    if code :
        return MessageChain(
            At(event.sender.id),
            "没找到相关内容，等会再试试吧"
            )
    ret=random.choice(data.data.list)
    ret.postData.postView.digest = ret.postData.postView.digest.replace('<p>' , '')
    ret.postData.postView.digest = await filter_tags(ret.postData.postView.digest)
    return MessageChain(
            At(event.sender.id),
            Image(url= ret.postData.postView.firstImage.orign),
            f"标题：《{ret.postData.postView.digest}》\n",
            f"作者：{ret.blogInfo.blogNickName}\n",
            f"热度：{ret.postData.postCount.favoriteCount}\n",
            f"原文地址：{ret.postData.postView.postPageUrl}"
            )

async def getTags(event,**args):
    code,data,raw = await getdata("newsearch/tag.json",args)
    if code :
        return MessageChain(
            At(event.sender.id),
            "没找到相关内容，等会再试试吧"
            )
    tags = ""
    for tag in data.data.tags:
        tags = tags + tag.tagName + " "
    return MessageChain(
            At(event.sender.id),
            f"找到存在这些标签：{tags}"
            )
    
async def getUserProfile(event,**args):
    code,data,raw = await getdata("newsearch/sug.json",args)
    if code :
        return MessageChain(
            At(event.sender.id),
            "没找到相关内容，等会再试试吧"
            )
            
    users="\n"
    for i in data.data.items:
        if i.type == 2:
            users = users + f"昵称：{i.blogData.blogInfo.blogNickName} 粉丝：{i.blogData.blogCount.followerCount} 文章数：{i.blogData.blogCount.publicPostCount} \n "
    return MessageChain(
            At(event.sender.id),
            users
            )
            
    
@lofter.use(ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(".lofter","老福特").help('老福特控制器'),
                    UnionMatch(
                        "-r","random",
                        "-t","tag",
                        "-s","search",
                        "-ST","SearchTag",
                        "-U","user",
                        "-h","help"
                    )@ "func",
                    WildcardMatch() @ "param",
                ]
            )
        ]
    )
)
async def loferfunc(app: Ariadne,
    message: MessageChain,
    event:GroupMessage,
    group: Group, 
    func: MatchResult, 
    param: MatchResult):
    func = func.result.display
    if func in ("-r","random"):data = await getHighHeatRandomPic(event)
    elif func in ("-t","tag","-s","search") and param.result.display: data = await getHighHeatRandomPic(event,tag = param.result.display)
    elif func in ("-ST","SearchTag") and param.result.display:data = await getTags(event,key=param.result.display)
    elif func in ("-U","user") and param.result.display:data = await getUserProfile(event,key=param.result.display)
    elif func in ("-h","help"):
        await app.send_message(
        group, 
        MessageChain(
            "欢迎使用LOFTER搜图功能哦\n",
            "您可以访问具体使用说明文档",
            config.docs + "help/lofter",
            "来获取更加详细的使用方法"
            )
        )
        return
    else:return
        
    await app.send_message(
             group,
            data
         )
