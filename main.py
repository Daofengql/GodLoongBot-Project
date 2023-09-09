from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (HttpClientConfig,
                                             WebsocketClientConfig)
from graia.ariadne.connection.config import config as ariadne_config
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.scheduler import GraiaScheduler
from graia.scheduler.saya.behaviour import GraiaSchedulerBehaviour

from library.config import config
from library.context import scheduler


import multiprocessing
from library.orm.extra import redis_db_pool
from aiohttp import web
from library.md2img import M2I
import time

m2i = M2I()
redis = redis_db_pool()


async def handle_md2img(request):
    id = request.match_info.get('id', 'default_id')  # 获取匹配到的id参数
    redis_client = await redis.get_redis_session()
    async with redis_client.client() as session:
        content = await session.get("md2img_"+id)
        if not content:
            text = m2i.tpl.format(str(f"{id} was not found"))
            return web.Response(text=text,status=404,content_type="text/html")
            
        else:
            text = m2i.tpl.format(str(content.decode()))
            return web.Response(text=text,status=200,content_type="text/html")

app = web.Application()
app.add_routes([web.get('/md2img/{id}', handle_md2img)])


ariadne = Ariadne(
    connection=ariadne_config(
        
        config.account,
        config.verify_key,
        HttpClientConfig(host=config.host),
        WebsocketClientConfig(host=config.host),
    )
)
saya = ariadne.create(Saya)
scheduler.set(ariadne.create(GraiaScheduler))
saya.install_behaviours(
    ariadne.create(BroadcastBehaviour),
    ariadne.create(GraiaSchedulerBehaviour),
)



def runaiohttp(app):
    print("staring HTTPSERVER.......")
    web.run_app(app,port=18000)



if __name__ == """__main__""":
    
    process = multiprocessing.Process(target=runaiohttp, args=(app,))
    process.start()
    
    time.sleep(2)
    from module import modules
    modules.require_modules(saya, log_exception=False)
    ariadne.launch_blocking()


    
