import time
from socket import *
from graia.ariadne.app import Ariadne
from ping3 import ping
 


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

async def pingip(arg):
    args = str(arg).strip()
    pingw = pings(args)
    info = await ipinfo(pingw['ip'])
    if info["code"]:
        try:
            addr = info["data"]["country"]
            city = info["data"]["isp"]
        except:addr = city = "查询失败"
    else:addr = city = "查询失败"
    rely = f"\nIP/域名：{pingw['host']}\n响应ip：{pingw['ip']}\n延迟：{pingw['delay']}\n物理地址：{addr}\nISP：{city}"
    return rely

async def tcpingip(host,port):
    
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
    
    
    rely = f"\nIP/域名：{host}\n指向ip：{ip_address}\n端口:{port}\n延迟：{time}\n物理地址：{addr}\nISP：{city}"
    return rely