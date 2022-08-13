import json

import httpx
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, MusicShareKind


class ObjectDict(object):
    def __init__(self, d): self.__d__ = d

    def __setattr__(self, key, value):
        if key == "__d__": return super.__setattr__(self, key, value)

        self.__d__.__setitem__(key, value)

    def __getattr__(self, item):
        if item == "__d__": return super.__getattr__(self, item)

        val = self.__d__.__getitem__(item)
        if isinstance(val, dict): return self.__class__(val)
        elif isinstance(val, list): return [self.__class__(d) for d in val]
        else: return val


async def get_netease(name: str, app, group, event):
    try:
        args = {"name": name, "pglimit": 10}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.s1.hanwuss.com/tools/et/song/netease",
                params=args,
                timeout=120,
            )
            if response.status_code != 200:  return None
        re = ObjectDict(json.loads(response.text))
        l = []
        for song in re.result.songs:
            l.append(
                {
                    "name": song.name,
                    "author": song.ar[0].name,
                    "id": song.id,
                    "pictureUrl": song.al.picUrl,
                }
            )
    except:  return None
    rely = ""
    count = 0
    for i in l:
        count += 1
        rely = rely + f"\n{count}. {i['name']}--{i['author']}"
    await app.send_message(
        group, MessageChain(At(event.sender.id), "\n为您找到如下歌曲，您可以回复序号进行点歌", rely)
    )
    return l


async def netease(l, select):
    song = l[select - 1]
    
    try:
        args = {"id": song["id"]}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.s1.hanwuss.com/tools/et/song/netease",
                params=args,
                timeout=120,
            )
            print(json.loads(response.text))
            if response.status_code != 200:  return None
            re = ObjectDict(json.loads(response.text))
        r = {
            "brief": f"{song['name']}--{song['author']}",
            "jumpUrl": f"https://music.163.com/song?id={song['id']}",
            "musicUrl": re.result[0].url,
            "pictureUrl": song["pictureUrl"],
            "summary": f"{song['name']}--{song['author']}",
            "title": song["name"],
            "kind": MusicShareKind.NeteaseCloudMusic,
        }
    except: return None
    return r
    
    
async def get_kugomusic(name,app, group, event):
    try:
        args = {"name": name, "pglimit": 10}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.s1.hanwuss.com/tools/et/song/kugou",
                params=args,
                timeout=120,
            )
            if response.status_code != 200:  return None
        re = ObjectDict(json.loads(response.text))
        l = []
        for song in re.result.info:
            l.append(
                {
                    "name": song.songname,
                    "author": song.singername,
                    "id": song.hash,
                }
            )
    except:  return None
    
    rely = ""
    count = 0
    for i in l:
        count += 1
        rely = rely + f"\n{count}. {i['name']}--{i['author']}"
    await app.send_message(
        group, MessageChain(At(event.sender.id), "\n为您找到如下歌曲，您可以回复序号进行点歌", rely)
    )
    return l
    
    
async def kugomusic(l, select):
    song = l[select - 1]
    
    try:
        args = {"hash": song["id"]}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.s1.hanwuss.com/tools/et/song/kugou",
                params=args,
                timeout=120,
            )
            if response.status_code != 200:  return None
        re = ObjectDict(json.loads(response.text))
        
        r = {
            "brief": f"{song['name']}--{song['author']}",
            "jumpUrl": f"http://m.kugou.com/play/info/{song['id']}",
            "musicUrl": re.url,
            "pictureUrl": re.album_img,
            "summary": f"{song['name']}--{song['author']}",
            "title": song["name"],
            "kind": MusicShareKind.KugouMusic,
        }
    except: return None
    return r   