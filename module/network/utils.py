import asyncio
import ipaddress
import json
import os
import re
import time
from io import BytesIO
from pathlib import Path
from socket import *

import aiohttp
import PIL.Image as PImage
import shodan
from aiocache import cached
from aiohttp import BasicAuth
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image, Plain, Source
from ping3 import ping

from library.image.oneui_mock.elements import (Banner, Column, GeneralBox,
                                               Header, OneUIMock)
from library.loongapi.models import Model_ret
from library.ToThread import run_withaio

PATH = Path(__file__).parent

if not os.path.exists(PATH / "shodanConf.json"):
    js = {
        "API_KEY":"你的api秘钥"
        }
    with open(PATH / "shodanConf.json","w") as f:
        js = json.dumps(js)
        f.write(js)
else:
    with open(PATH / "shodanConf.json","r") as f:
        SDapi = shodan.Shodan(json.loads(f.read())["API_KEY"])



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
            
            
async def ipinfo(args)->Model_ret:
    session = Ariadne.service.client_session
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
    url = f"https://v1.loongapi.com/v1/tool/ip/info?addr={args}"
    async with session.get(url, headers = headers,timeout=120) as response1:
        r = Model_ret.parse_obj(await response1.json())
        return r


@cached(ttl=300)
async def pingip(arg)->MessageChain:
    args = str(arg).strip()
    pingw = pings(args)
    info = await ipinfo(pingw['ip'])
    if info.code == 200:
        try:
            addr = info.result.cz88.address
            city = info.result.cz88.isp
        except:addr = city = "查询失败"
    else:addr = city = "查询失败"

    column = Column(Banner("Ping查询"), Header("查询返回", "基于位于圣何塞的机器人检测网络返回数据"))
    box = GeneralBox()
    box.add(f"IP/域名：{pingw['host']}","")
    box.add(f"响应ip：{pingw['ip']}","")
    box.add(f"延迟：{pingw['delay']}","")
    box.add(f"物理地址：{addr}","")
    box.add(f"ISP：{city}","")
    column.add(box)
    mock = OneUIMock(column)
    rendered_bytes = await run_withaio(mock.render_bytes,args=())
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
    if info.code == 200:
        try:
            addr = info.result.cz88.address
            city = info.result.cz88.isp
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
    rendered_bytes = await run_withaio(mock.render_bytes,args=())

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
    rendered_bytes = await run_withaio(mock.render_bytes,args=())
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
        rendered_bytes = await run_withaio(mock.render_bytes,args=())
        return MessageChain(Image(data_bytes=rendered_bytes))


async def aton(addr)->MessageChain:
    try:
        ip_address = gethostbyname(addr)
        tip = int(ipaddress.IPv4Address(ip_address))
        bip = str(bin(tip))[2:]
        bip=re.findall(r'.{8}',bip) 
        bip=' '.join(bip) 
    except:
        ip_address = "域名或ip解析错误"
        tip = "域名或ip解析错误"
        bip = "域名或ip解析错误"
    
    return MessageChain(
        Plain(f"转换前ip:{ip_address}\n"),
        Plain(f"十进制转换:{tip}\n"),
        Plain(f"二进制转换:{bip}")
    )

@cached(ttl=3600*24)
async def icp(
    domain
)->MessageChain:
    session = Ariadne.service.client_session

    column = Column(Banner("备案查询"), Header("查询返回", ""))
    

    async with session.get(f'https://api.vvhan.com/api/icp?url={domain}') as response:
        result:dict = await response.json(content_type="text/html")

        if not result.get("success"):
            box = GeneralBox()
            box.add(f"域名：{domain} 未备案","请检查是否填写的为根域名而非子域名")
            column.add(box)
            mock = OneUIMock(column)
        else:
            box1 = GeneralBox()
            async with session.get(f"https://api.vvhan.com/api/ico?url={domain}") as resp:
                img = PImage.open(BytesIO(await resp.content.read()))
            column.add(img)
            column.add(box1)
            mock = OneUIMock(column)
        rendered_bytes = await asyncio.to_thread(mock.render_bytes)
        return MessageChain(Image(data_bytes=rendered_bytes))


@cached(ttl=1200)
async def ShodanSearchIP(
    ip
    )->MessageChain:
    
    try:
        info:dict = await asyncio.to_thread(SDapi.host,ips=ip)
    except Exception as e:
        return MessageChain(Plain("查询错误，未找到此地址的信息，您有可能搜索了一个内网ip或者环路ip"))

    #基础信息查询
    column = Column(Banner("IP信息查询  数据源：ShodanAPI"),)

    #图标
    async with aiohttp.ClientSession() as session:
        async with session.get("https://pic3.zhimg.com/v2-4f84ebc0f73ffac6b28ec460a2f5c43b_1440w.jpg") as resp:
            img = PImage.open(
                BytesIO(
                    await resp.content.read()
                )
            ).convert("RGBA")
            column.add(img)
    column.add(Header("基础信息", "显示运营商、地理信息等"))
    IPInfoBox = GeneralBox()
    IPInfoBox.add(f"AS:{info['asn']}","AS自治号")
    IPInfoBox.add(f"位置:{info['country_name']}-{info['city']} ({info['country_code']})","地理位置")
    IPInfoBox.add(f"ISP:{info.get('isp')}","运营商名")
    IPInfoBox.add(f"所属组织:{info.get('org')}","所属组织名")
    IPInfoBox.add(f"经纬:{info.get('longitude')},{info.get('latitude')}","地理坐标位置")
    IPInfoBox.add(f"OS:{info.get('os')}","疑似运行的操作系统")
    IPInfoBox.add(f"更新时间:{info.get('last_update')}","最后一次更新时间")

    if info.get('ports'):
        p = ""
        for port in info.get('ports'):
            p += f"[{port}] "
        IPInfoBox.add(f"端口:{p}","已知开放的端口")

    if info.get('tags'):
        t = ""
        for tag in info.get('tags'):
            t += f"{tag} "
        IPInfoBox.add(f"行为标签:{t}","推测行为标签数据")
    column.add(IPInfoBox)


    #漏洞信息
    
    column2 = Column(Header("漏洞信息", "可能存在的CVE漏洞情况"))
    vulnBox = GeneralBox()
    if info.get('vulns'):
        
        count = 1
        for vuln in info.get('vulns'):
            vulnBox.add(f"{count}. {vuln}","")
            count += 1
    else:
        vulnBox.add(f"暂未发现CVE漏洞","")
    column2.add(vulnBox)




    
    #域名信息
    column2.add(Header("域名信息", "已知包含解析到此ip的域名和此主机绑定的主机名"))
    DomainInfoBox = GeneralBox()
    if info.get('domains'):
        for domain in info.get('domains'):
            DomainInfoBox.add(f"域名:{domain}","已知解析过此ip")
    if info.get('hostnames'):
        for hostname in info.get('hostnames'):
            DomainInfoBox.add(f"主机:{hostname}","已知此ip对外宣称的主机名")
    column2.add(DomainInfoBox)


    mock = OneUIMock(column,column2)

    #端口信息
    idata:list[dict] = info.get('data')

    idatas:list[list[dict]] = [idata[i:i + 4] for i in range(0, len(idata), 4)]

    for idata in idatas:
        column3 = Column(Header("端口信息", "已知端口的监听业务服务情况（有缩减）"))
        PortInfoBox = GeneralBox()
        for Iport in idata:
            PortInfoBox.add(f"{Iport.get('transport')}:{Iport.get('port')} /{Iport.get('product')}",f"更新时间{Iport.get('timestamp')}\n回显数据(前300字符)：\n{Iport.get('data')[:300]}....")
        column3.add(PortInfoBox)
        mock.add(column3)

    rendered_bytes = await asyncio.to_thread(mock.render_bytes)

    return MessageChain(Image(data_bytes=rendered_bytes))

@cached(ttl=1200)
async def ShodanSearchQuery(
    query
    )->MessageChain:

    try:
        info:dict = await asyncio.to_thread(SDapi.search,query=query,limit=20)
    except Exception as e:
        return MessageChain(Plain("查询错误，可能是一个错误的搜索语法"))

    mock = OneUIMock()
    idata:list[dict] = info.get('matches')
    idatas:list[list[dict]] = [idata[i:i + 4] for i in range(0, len(idata), 4)]
    for idata in idatas:
        column = Column(Banner("Shodan查询   数据源：ShodanAPI"), Header("查询返回", "仅显示前几"))
        sInfoBox = GeneralBox()
        for i in idata:

            sInfoBox.add(f"{i.get('ip_str')}:{i.get('port')} /{i.get('product')} ({i.get('asn')})",f"回显数据(前300字符)：\n{i.get('data')[:300]}....")
        column.add(sInfoBox)
        mock.add(column)

    rendered_bytes = await asyncio.to_thread(mock.render_bytes)

    return MessageChain(Image(data_bytes=rendered_bytes))

P = Path(__file__).parent / "mqttserver.json"

if not os.path.exists(P):
    js = {
    "user": "",
    "pwd": ""
}
    with open(P,"w") as f:
        js = json.dumps(js)
        f.write(js)
else:
    with open(P,"r") as f:
        js = json.loads(f.read())
        mqttpwd = js["pwd"]
        mqttuser = js["user"]
        del js

