import time
from socket import *
from graia.ariadne.app import Ariadne
from ping3 import ping
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image, Source, Plain
from library.image.oneui_mock.elements import Column,GeneralBox,Banner,Header,OneUIMock
from aiocache import cached
import asyncio

import re


pattern = re.compile(r'[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?')


class tcping(object):
    def tcping(self, ip, port):
        tcp_client_socket = socket(AF_INET, SOCK_STREAM)
        try:
            start_time = time.time() * 1000
            tcp_client_socket.connect((str(ip), int(port)))
        except:
            return float(20000)
        stop_time = time.time() * 1000
        tcp_client_socket.close()
        return round(float(stop_time - start_time), 2)
tpi = tcping() 

def pings(args):
    try:  ip_address = gethostbyname(args)
    except:   return {"host":args,"ip":args,"code":"1","delay":"错误的地址没法解析"}
    else:
        response = ping(ip_address)
        if response is not None: return {"host":args,"ip":ip_address,"delay":str(int(response * 1000))+"ms","code":"0"}
        else:  return {"host":args,"ip":ip_address,"delay":"超时或禁ping","code":"1"}
            
            
async def ipinfo(args):
    session = Ariadne.service.client_session
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
    url = f"https://api.s1.hanwuss.com/tools/net/ip/address?ip={args}"
    async with session.get(url, headers = headers,timeout=120) as response1:
        return {"code":1,"Msg":"成功","data":(await response1.json())["info"]}


@cached(ttl=300)
async def pingip(arg)->MessageChain:
    args = str(arg).strip()
    pingw = pings(args)
    info = await ipinfo(pingw['ip'])
    if info["code"]:
        try:
            addr = info["data"]["country"]
            city = info["data"]["isp"]
        except:addr = city = "查询失败"
    else:addr = city = "查询失败"

    column = Column(Banner("Ping查询"), Header("查询返回", "基于位于东京的机器人检测网络返回数据"))
    box = GeneralBox()
    box.add(f"IP/域名：{pingw['host']}","")
    box.add(f"响应ip：{pingw['ip']}","")
    box.add(f"延迟：{pingw['delay']}","")
    box.add(f"物理地址：{addr}","")
    box.add(f"ISP：{city}","")
    column.add(box)
    mock = OneUIMock(column)
    rendered_bytes = await asyncio.gather(asyncio.to_thread(mock.render_bytes))
    rendered_bytes= rendered_bytes[0]
    return MessageChain(
        Image(data_bytes=rendered_bytes)

    )


@cached(ttl=300)
async def tcpingip(host,port)->MessageChain:
    
    time = tpi.tcping(host,int(port))#取得端口延迟
    #解析域名或ip得到实际ip
    try:ip_address = gethostbyname(host)
    except:ip_address ="解析失败"
    if abs(time) >=20000:time = "tcping超时"
    else:time = f"{time}ms"
    
    info = await ipinfo(ip_address)
    if info["code"]:
        try:
            addr = info["data"]["country"]
            city = info["data"]["isp"]
        except:addr = city = "查询失败"
    else:addr = city = "查询失败"
    
    column = Column(Banner("Tcping查询"), Header("查询返回", "基于位于东京的机器人检测网络返回数据"))
    box = GeneralBox()
    box.add(f"IP/域名：{host}","")
    box.add(f"指向ip：{ip_address}","")
    box.add(f"端口:{port}","")
    box.add(f"延迟：{time}","")
    box.add(f"物理地址：{addr}","")
    box.add(f"ISP：{city}","")
    column.add(box)
    mock = OneUIMock(column)
    rendered_bytes = await asyncio.gather(asyncio.to_thread(mock.render_bytes))
    rendered_bytes= rendered_bytes[0]
    return MessageChain(
        Image(data_bytes=rendered_bytes)

    )



@cached(ttl=1200)
async def dnsrecord(
    domain, 
    ip
    )->MessageChain:

    par = {"name":domain}
    
    box = GeneralBox()
    if ip and pattern.search(ip):
        par["edns_client_subnet"] = pattern.search(ip).group()
        box.add("使用了特定的公网地址查询解析", f"地址：{pattern.search(ip).group()}")
    
    
    column = Column(Banner("DNS查询"), Header("查询返回", "基于寒武天机的全球DOH检测网络返回数据"))
    
    session = Ariadne.service.client_session
    async with session.get('https://dns.alidns.com/resolve',params=par) as response:
        result = await response.json()
        try:
            if result["code"]:box.add("检测错误", result["code"])
        except:pass
        try:
            for res in result["Answer"]:
                if res['type'] == 1:typ = "A"
                elif res['type'] == 5 :typ = "CNAME"
                elif res['type'] == 6 :typ = "NS"
                else:typ = "其他"
                box.add(f"响应：{res['data']}  TTL={res['TTL']}",f"上级节点：{res['name']} 解析类型：{typ}")
        except:box.add("检测错误","")
    column.add(box)
    mock = OneUIMock(column)
    rendered_bytes = await asyncio.gather(asyncio.to_thread(mock.render_bytes))
    rendered_bytes= rendered_bytes[0]
    return MessageChain(Image(data_bytes=rendered_bytes))



@cached(ttl=3600*24)
async def whois(
    domain
)->MessageChain:
    session = Ariadne.service.client_session

    column = Column(Banner("Whois查询"), Header("查询返回", "基于DnspodAPI返回数据"))
    

    async with session.post('https://www.dnspod.cn/cgi/qcwss?action=getWhoisInfo',json={"domain":domain}) as response:
        result:dict = await response.json()
        result = result["result"]

        if "Error" in result:
            box = GeneralBox()
            box.add("检测错误","")
            column.add(box)
            mock = OneUIMock(column)
        else:
            box1 = GeneralBox()
            box2 = GeneralBox()
            result = result["WhoisInfo"]
            dns = ""
            for tmp in result["DnsServer"]:
                dns = dns+tmp+"\n"
            box1.add(f"Dns服务器：\n{dns}","DnsServer")

            Registrar = ""
            for tmp in result["Registrar"]:
                Registrar = Registrar+tmp+"\n"
            box1.add(f"注册商：\n{Registrar}","Registrar")

            box1.add(f"注册时间：{result['RegistrationDate']}","RegistrationDate")
            box1.add(f"到期时间：{result['ExpirationDate']}","ExpirationDate")

            RegistrantEmail = ""
            for tmp in result["RegistrantEmail"]:
                RegistrantEmail = RegistrantEmail+tmp+"\n"
            box1.add(f"注册邮箱：\n{RegistrantEmail}","RegistrantEmail")

            box1.add(f"DNSSEC状态：{result['DNSSEC']}","DNSSEC")

            DomainStatus = ""
            for tmp in result["DomainStatus"]:
                DomainStatus = DomainStatus+tmp+"\n"
            box1.add(f"域名状态：\n{DomainStatus}","DomainStatus")

            box2.add(f"RAW：\n{result['Raw'][0]}","原始注册信息")

            column.add(box1)
            column.add(box2)
            mock = OneUIMock(column)
        rendered_bytes = await asyncio.gather(asyncio.to_thread(mock.render_bytes))
        rendered_bytes= rendered_bytes[0]
        return MessageChain(Image(data_bytes=rendered_bytes))


