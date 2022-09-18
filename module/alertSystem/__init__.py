import asyncio
import aiofiles

import aiohttp

from graia.ariadne.app import Ariadne

from collections import deque
from graia.ariadne.message.element import Image, At, Plain, Source, AtAll
from graia.ariadne.model import Group
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from graia.saya import Channel
from .data import get_sub_group,parse_data

aleater = Channel.current()


INIT_LIST = deque(maxlen=150)

async def init():
    global INIT_LIST
    async with aiohttp.ClientSession() as session:
            
        async with session.get("http://www.ceic.ac.cn/daochu/id:1") as response:
            x1 = await response.text()

        INIT_LIST = await parse_data(x1)



loop = asyncio.get_event_loop()
loop.run_until_complete(init())

@aleater.use(SchedulerSchema(timers.every_custom_seconds(10)))
async def every_minute_speaking(app: Ariadne):
    global INIT_LIST

    session = Ariadne.service.client_session

    subgroup = await get_sub_group("eq")
    
    async with session.get("http://www.ceic.ac.cn/daochu/id:1") as response:
        x2 = await response.text()

    x2 = await parse_data(x2)

    for i in x2:
        if i not in INIT_LIST:
            INIT_LIST.append(i)
            message = f"根据中国地震台网速报：{i['time']} 在 {i['addr']} （{i['longitude']}° {i['latitude']}°）发生里氏 {i['level']}级地震，震源深度{i['depth']}KM \n本数据来源中国地震台网，http://www.ceic.ac.cn，正式数据以官方通知为准"
            
            for group in subgroup:
                await app.send_group_message(
                    target=group,
                    message=message
                )
            
            
            