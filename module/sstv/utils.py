from aiocache import cached
from io import BytesIO
from graiax import silkcoder
from library.ToThread import run_withaio
import aiohttp
#莫斯密码部分

import pypinyin 
 
# 给字典赋值
# 字母转码
dict1 = {'a':'.-'  ,'b':'-...','c':'-.-.','d':'-..'  ,'e':'.',
        'f':'..-.','g':'--.' ,'h':'....','i':'..'  ,'j':'.---',
        'k':'-.-' ,'l':'.-..','m':'--'  ,'n':'-.'  ,'o':'---' ,
        'p':'.--.','q':'--.-','r':'.-.' ,'s':'...' ,'t':'-'   ,
        'u':'..-' ,'v':'...-','w':'.--' ,'x':'-..-','y':'-.--','z':'--..',
        '0':'-----' ,'1':'.----' ,'2':'..---' ,'3': '...--','4': '....-' ,
        '5': '.....','6': '-....','7': '--...','8': '---..','9': '----.', 
        ', ':'--..--', '.':'.-.-.-',
        '?':'..--..', '/':'-..-.', '-':'-....-',
        '(':'-.--.', ')':'-.--.-'}

# 码转字母
dict2 = dict(zip(dict1.values(),dict1.keys()))
# 中文转拼音
@cached(ttl=30000)
async def chinese_to_pinyin(strs):
    strs = strs.strip().lower()
    temp = ''
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            result1 = pypinyin.pinyin(_char, style=pypinyin.NORMAL)
            result2 = [i[0] for i in result1]
            result3 = ''.join(result2[:])
            temp += result3 + ' '
        else:
            temp += _char 
    return temp
 
# 文字转码
@cached(ttl=30000)
async def encode(words):
    r = ""
    for letter in words:
        if letter in dict1:
            r = r + dict1[letter] + "/"
    return r

HEAD = {
    "Content-type":"application/json"
}

@cached(ttl=30000)
async def genMORSvoice(words,codeMulti=0,splitMulti=1)->bytes:
    words = await chinese_to_pinyin(words)
    words = await encode(words)
    js = {"morseCode":words,"codeMulti":codeMulti,"splitMulti":splitMulti}
    async with aiohttp.ClientSession() as session:
        async with session.post("https://www.lddgo.net/api/MorseCode",json=js,headers=HEAD) as resp:
            res = await resp.json()
        async with session.get(res["data"],headers=HEAD) as resp:
            d = await resp.content.read()
            audio_bytes = await silkcoder.async_encode(d, ios_adaptive=False)
    return audio_bytes

#sstv部分
import PIL.Image as PIMG

from pysstv.color import (
    MartinM1,
    MartinM2,
    Robot36,
    ScottieS1,
    ScottieS2
)

from graia.ariadne.message.parser.twilight import MatchResult     

@cached(ttl=30000)
async def gentoSSTV(mod: MatchResult,imgdata):
    if mod.matched:
        mod = mod.result.display
    else:
        mod = "M1"
    ret = BytesIO()
    img = PIMG.open(
        BytesIO(
                imgdata
            )).convert("RGB")

    img = img.resize((320,int((320/img.width)*img.height)))
    if mod == "M1":
        a = MartinM1(image=img,samples_per_sec=48000,bits=16)
    elif mod == "M2":
        a = MartinM2(image=img,samples_per_sec=48000,bits=16)
    elif mod == "R36":
        a = Robot36(image=img,samples_per_sec=48000,bits=16)
    elif mod == "S1":
        a = ScottieS1(image=img,samples_per_sec=48000,bits=16)
    elif mod == "S2":
        a = ScottieS2(image=img,samples_per_sec=48000,bits=16)
    else:
        a = MartinM1(image=img,samples_per_sec=48000,bits=16)

    await run_withaio(a.write_wav, args=(ret,))
    ret.seek(0)
    audio_bytes = await silkcoder.async_encode(ret.read(), ios_adaptive=True)
    return audio_bytes