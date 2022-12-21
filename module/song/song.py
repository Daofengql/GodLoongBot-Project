from graia.ariadne import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, MusicShareKind

from library.loongapi.models import Model_ret, SongChoices
from graia.ariadne.message.element import MusicShare


async def get_netease(name: str, app, group, event):
    session = Ariadne.service.client_session
    try:
        args = {"name": name, "pglimit": 10}
        async with session.get(
            "https://v1.loongapi.com/v1/bot/musicChoose/netease",params=args ,timeout=120) as response:
            if response.status != 200:  return None
            re = Model_ret.parse_obj(await response.json())
        l = re.result.songs
    except:  return None
    rely = ""
    count = 0
    for i in l:
        count += 1
        rely = rely + f"\n{count}. {i.name}--{i.author[0].name}"
    await app.send_message(
        group, MessageChain(At(event.sender.id), "\n为您找到如下歌曲，您可以回复序号进行点歌", rely)
    )
    return l


async def netease(l, select):
    song:SongChoices.Song_types.Song_netease = l[select - 1]
    
    return MusicShare(
        brief=f"{song.name}--{song.author[0].name}",
        jumpUrl=f"https://music.163.com/song?id={song.id}",
        kind=MusicShareKind.NeteaseCloudMusic,
        musicUrl=song.songurl,
        pictureUrl= song.picurl,
        summary=f"{song.name}--{song.author[0].name}",
        title=song.name,
    )