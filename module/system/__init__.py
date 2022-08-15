from graia.ariadne.event.message import GroupMessage
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.base import MatchRegex
from graia.ariadne.model import Group
from graia.ariadne.message.element import At,Image,Source
import httpx
import os
import asyncio
from library.TextToImg import TextToImage
import os,socket,time
import psutil ,asyncio
import json
import time as te
from library.config import config


cmd = Channel.current()

cmd.name("shell插件")
cmd.author("道锋潜鳞")
cmd.description("使用群消息作为终端执行shell命令")

def cmdline(cmds):
    f = os.popen(str(cmds),"r")
    return f.read()
maker = TextToImage()


@cmd.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchRegex(regex=r"^.cmd ")]
        )
    )
async def runcmd(
    app: Ariadne,
    message: MessageChain,
    event:GroupMessage,
    group: Group):
    if event.sender.id not in config.owners:
        await app.send_message(
             group,
            MessageChain(At(event.sender.id),f"你好像不是{config.name}的最高管理员，没有权限使用本命令哦")
         )
        return
    args = str(message.display).strip()[5:]
    try:
        back = await asyncio.gather(asyncio.to_thread(cmdline,args))
        back = str("以下内容由服务器直接返回：\n"+back[0])
        dat = await asyncio.gather(asyncio.to_thread(maker.create_image,back,130))
        dat = dat[0]
        await app.send_message(
             group,
            MessageChain(Image(data_bytes=dat))
         )

    except:
        await app.send_message(
             group,
            MessageChain(At(event.sender.id),f"系统命令执行错误了")
         )
        return
    
        
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}    
async def getNetworkinfo():
    time1 = {"timeout":0,"success":0,"avrage":0,"temp":[]}
    for i in [1,2]:
        try:
            start_time = te.time()* 1000
            async with httpx.AsyncClient() as client:
                response1 = await client.get("https://api.s1.hanwuss.com/", headers = headers)
                json.loads(response1.text)
            stop_time = te.time()* 1000
            time = round(float(stop_time-start_time), 2)
            time1["success"] += 1
        except:
            time1["timeout"] += 1
            time = float(20000)
        time1["temp"].append(time)
    t = 0
    for time in time1["temp"]:  t+=time
    time1["avrage"] = round(float(t/2), 2)
    return time1

async def getFileSize(filePath, size=0):
    for root, dirs, files in os.walk(filePath):
        for f in files:  size += os.path.getsize(os.path.join(root, f))
    size = "机器人缓存目录占用：%0.2fM" % (size / 1024. / 1024.)
    return size

# cpu信息
async def get_cpu_info():
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_info = "CPU使用率：%i%%" % cpu_percent
    return cpu_info

async def get_cpu_info_2():
    start_time ='服务器开机的时间是:{}\n'.format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(psutil.boot_time())))
    pCPU = '服务器计算CPU个数:{}个\n'.format(psutil.cpu_count())
    vCPU = '服务器插槽CPU个数:{}个'.format(psutil.cpu_count(logical=False))
    return start_time + pCPU + vCPU
# 内存信息
async def get_memory_info():
    virtual_memory = psutil.virtual_memory()
    used_memory = virtual_memory.used/1024/1024/1024
    free_memory = virtual_memory.free/1024/1024/1024
    memory_percent = virtual_memory.percent
    memory_info = "内存使用：%0.2fG，使用率%0.1f%%，剩余内存：%0.2fG" % (used_memory, memory_percent, free_memory)
    return memory_info

async def get_current_memory():
# 获取当前进程内存占用。
    pid = os.getpid()
    p = psutil.Process(pid)
    info = p.memory_full_info()
    memory = "当前机器人占用内存大小：%0.2fM" % (info.uss / 1024. / 1024.)
    return memory
#获取本地ip
async def get_local_ip():
    local_ip = ""
    try:
        socket_objs = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]
        ip_from_ip_port = [(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in socket_objs][0][1]
        ip_from_host_name = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1]
        local_ip = [l for l in (ip_from_ip_port, ip_from_host_name) if l][0]
    except (Exception) as e:  print("get_local_ip found exception : %s" % e)
    return local_ip if("" != local_ip and None != local_ip) else socket.gethostbyname(socket.gethostname())

async def getdata():
    current = await get_current_memory()
    mem = await get_memory_info()
    cpus = await get_cpu_info()
    tmpf = os.path.dirname(os.getcwd())+'/tmp'
    FolderSize = await getFileSize(tmpf)
    cpus2 = await get_cpu_info_2()
    netinfo = await getNetworkinfo()
    rely = f"{current}\n{mem}\n{cpus}\n{cpus2}\n机器人运行目录：{os.getcwd()}\n机器人缓存目录：{tmpf}\n{FolderSize}\n云中心链接速度：平均延迟{netinfo['avrage']}ms,共测试2次，错误{netinfo['timeout']}次，成功{netinfo['success']}次"
    if netinfo['timeout']>1 or netinfo['avrage']>500: rely = rely +"\n云中心链接不稳定，请注意"
    return rely
   
   
@cmd.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchRegex(regex=r"^.status")]
        )
    )
async def runcmd(
    app: Ariadne,
    event:GroupMessage,
    group: Group):
    if event.sender.id not in config.owners:
        await app.send_message(
             group,
            MessageChain(At(event.sender.id),f"你好像不是{config.name}的最高管理员，没有权限使用本命令哦")
         )
        return
    try:
        
        await app.send_message(
             group,
            MessageChain(await getdata())
         )

    except:
        await app.send_message(
             group,
            MessageChain(At(event.sender.id),f"系统命令执行错误了")
         )
        return

@cmd.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchRegex(regex=r"^上传图床")]
        )
    )
async def runcmd(
    app: Ariadne,
    message: MessageChain,
    event:GroupMessage,
    group: Group):
    
    l = message.get(Image)
    s = ""
    if not l:
        await app.send_group_message(
            group,
            
            MessageChain(
                At(event.sender.id),
                "没看到你发了什么图嗷，跟在命令后面再试试吧"
            ),
            quote=event.message_chain.get_first(Source)
            
        )
        return
    elif len(l)>10:
        await app.send_group_message(
            group,
            MessageChain(At(event.sender.id),"太多了，一次只能10个哦~"),
            quote=event.message_chain.get_first(Source)
            
        )
        return

    for i in l:
        s = s +f"{i.url}\n"

    await app.send_group_message(
            group,
            MessageChain(At(event.sender.id),f"\n{s}上传好了哦"),
            quote=event.message_chain.get_first(Source)
            
        )
