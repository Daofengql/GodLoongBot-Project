from graia.ariadne.event.message import GroupMessage
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.model import Group
from graia.ariadne.message.element import At,Image
from library.Bot import bot
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    ElementMatch,
    ElementResult,
    ParamMatch
)
import datetime
import random
petpeter = Channel.current()
petpeter.name("petpeter插件")
petpeter.author("道锋潜鳞")
petpeter.description("生成表情包动图")


BOT = bot()
LAST_QEQUEST = datetime.datetime.now()
async def get_simple_data(func,**data):
    session = Ariadne.service.client_session
    ROOT_URL = "https://v1.loongapi.com/v1/bot/MEMEs/petpeter/"
    url = ROOT_URL + func
    for i in BOT.weijingci:
        for k in data:
            if i in str(data[k]):return (3,"生成暂停，您的参数含有违禁词")
    try:
        async with session.get(url, params=data,timeout=120) as response:
            if response.status!= 200:  return (1,None)
            try:
                if response.headers['X-Scf-Message'] == 'MemoryLimitReached':return (2,"生成失败，进程内存超额")
            except: pass
            return (0,await response.read())
    except: return (1,"获取数据错误")

async def limit_check():
    global LAST_QEQUEST
    nowtime = datetime.datetime.now()
    if (nowtime-LAST_QEQUEST) > datetime.timedelta(seconds = 15):
        LAST_QEQUEST = datetime.datetime.now()
        return True
    return False
    
    
                
@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("rua").help('获取rua某人的图片'),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
async def rua(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    target = message.get(At)[0].target
    status,result = await get_simple_data(func="rua",qid=target)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         )
         

@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("kisskiss").help('获取kiss某人的图片'),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    ElementMatch(At),
                    UnionMatch("kisskiss").help('获取kiss某人的图片'),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
async def kiss(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    if len(target)<2:
        qid2=event.sender.id
        qid1=target[0].target
        
    else:
        qid1=target[0].target
        qid2=target[1].target
    status,result = await get_simple_data(func="kisskiss",qid1=qid1,qid2=qid2)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         )
    



@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("rub").help('获取rub某人的图片'),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("rub").help('获取rub某人的图片'),
                    ElementMatch(At),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
async def rub(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    if len(target)<2:
        qid2=event.sender.id
        qid1=target[0].target
        
    else:
        qid1=target[0].target
        qid2=target[1].target
    status,result = await get_simple_data(func="rub",qid=qid1,qid2=qid2)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         )
  
  
         
@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("petplay").help('获取玩耍某人的图片'),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
async def petplay(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    status,result = await get_simple_data(func="play",qid=qid1)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         )
         
         
@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("petpat").help('获取pat某人的图片'),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
async def pat(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    status,result = await get_simple_data(func="pat",qid=qid1)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         )  


@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("throw").help('获取throw某人的图片'),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
async def throw(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    status,result = await get_simple_data(func="throw",qid=qid1,gif=True)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         )     
    
    

@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("crawl","爬").help('获取crawl某人的图片'),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
async def crawl(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    crawl_num = random.randint(1,92)
    status,result = await get_simple_data(func="crawl",qid=qid1,crawl_num=crawl_num)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         )   
         

@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("always","一直").help('获取crawl某人的图片'),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
async def always(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    status,result = await get_simple_data(func="always",qid=qid1)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         ) 
         
         
@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("support","精神支柱").help('获取support某人的图片'),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
async def support(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    status,result = await get_simple_data(func="support",qid=qid1)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         )
         
         
         
@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("littleangel","小天使").help('他真的太可爱了，简直是个小天使'),
                    ElementMatch(At),
                    "name" @ ParamMatch(),
                ]
            )
        ]
        )
    )
    
async def littleangel(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group,name:ElementResult):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    name1 = str(name.result)
    name = await app.get_user_profile(qid1)
    if name.sex == "MALE":ta = "他"
    elif name.sex == "FEMALE":ta = "她"
    else:ta = "它"
    if not name1:
        await app.send_message(
             group,
            MessageChain("参数好像不完整哦")
         )
        return
    elif len(name1)>10:
        await app.send_message(
             group,
            MessageChain("参数好像太长了哦")
         )
        return
    status,result = await get_simple_data(func="littleangel",qid=qid1,name=name1,ta=ta)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         ) 
@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("littleangel","小天使").help('他真的太可爱了，简直是个小天使'),
                    ElementMatch(At),
                ]
            )
        ]
        )
    )
async def littleangel2(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    name = await app.get_user_profile(qid1)
    if name.sex == "MALE":ta = "他"
    elif name.sex == "FEMALE":ta = "她"
    else:ta = "它"
    name = name.nickname
    status,result = await get_simple_data(func="littleangel",qid=qid1,name=name,ta=ta)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         )          

         
         
         
@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("turn","转圈圈").help('获取turn某人的图片'),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
async def turn(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    status,result = await get_simple_data(func="turn",qid=qid1)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         )


@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("playgame","来玩游戏").help('来玩游戏呀'),
                    ElementMatch(At),
                    "data" @ ParamMatch(),
                ]
            )
        ]
        )
    )
    
async def playgame(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group,data:ElementResult):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    data = str(data.result)
    if not data:
        await app.send_message(
             group,
            MessageChain("参数好像不完整哦")
         )
        return
    elif len(data)>10:
        await app.send_message(
             group,
            MessageChain("参数好像太长了哦")
         )
        return
    status,result = await get_simple_data(func="playgame",qid=qid1,text=data)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         ) 
@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("playgame","来玩游戏").help('来玩游戏呀'),
                    ElementMatch(At),
                ]
            )
        ]
        )
    )
async def playgame2(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    status,result = await get_simple_data(func="playgame",qid=qid1)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         )   
         
         
         
@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("worship","拜拜").help('获拜拜某人的图片'),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
async def worship(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    status,result = await get_simple_data(func="worship",qid=qid1)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         )


@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("peteat","吃你").help('获吃某人的图片'),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
async def eat(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    status,result = await get_simple_data(func="eat",qid=qid1)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         )
         
         
         
@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("petroll","滚雪球").help('获滚雪球某人的图片'),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
async def roll(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    status,result = await get_simple_data(func="roll",qid=qid1)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         )
         
         
@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("petpolice","条子").help('获滚某人的条子图片'),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
async def police(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    status,result = await get_simple_data(func="police",qid=qid1)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         )
         
@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("petbite","吃掉你").help('获取吃掉某人的图片'),
                    ElementMatch(At)
                ]
            )
        ]
        )
    )
async def bite(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    status,result = await get_simple_data(func="bite",qid=qid1)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
                  ) 
                  
                  
                  
@petpeter.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("让").help('让他告诉你'),
                    ElementMatch(At),
                    UnionMatch("告诉你").help('让他告诉你')
                ]
            )
        ]
        )
    )
async def ask(app: Ariadne,message: MessageChain,event:GroupMessage,group: Group):
    if not await limit_check():
        await app.send_message(
             group,
            MessageChain("这个功能刚刚已经被其他用户使用了，15秒内暂时没法使用哦，稍等再试试吧~~")
         )
        return
    
    target = message.get(At)
    qid1=target[0].target
    name = await app.get_user_profile(qid1)
    if name.sex == "MALE":ta = "他"
    elif name.sex == "FEMALE":ta = "她"
    else:ta = "它"
    name = name.nickname
    status,result = await get_simple_data(func="ask",qid=qid1,name=name,ta=ta)
    if status :
        await app.send_message(
             group,
            MessageChain(result)
         )
        return
    await app.send_message(
             group,
            MessageChain(Image(data_bytes=result))
         )          
