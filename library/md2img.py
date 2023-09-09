import aiohttp
import asyncio
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html
from library.orm.extra import redis_db_pool
import uuid

redis = redis_db_pool()

class M2I:
    class HighlightRenderer(mistune.HTMLRenderer):
        def block_code(self, code, info=None):
            if info:
                try:
                    lexer = get_lexer_by_name(info, stripall=True)
                except:
                    lexer = get_lexer_by_name('text', stripall=True)
                formatter = html.HtmlFormatter()
                return highlight(code, lexer, formatter)
            return '<pre><code>' + mistune.escape(code) + '</code></pre>'


    def __init__(self) -> None:
        self.markdown = mistune.create_markdown(renderer=self.HighlightRenderer())
        self.tpl = """
        <html lang="zh" class="js-focus-visible js" data-js-focus-visible="">
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>神麟-生成器页面</title>
        <link rel="stylesheet" href="https://objectstorage.global.loongapi.com/loongapiSources/media/bot/t2i/assets/stylesheets/main.85bb2934.min.css">
        <link rel="stylesheet" href="https://objectstorage.global.loongapi.com/loongapiSources/media/bot/t2i/assets/stylesheets/palette.a6bdf11c.min.css">
        <link rel="stylesheet" href="https://objectstorage.global.loongapi.com/loongapiSources/media/bot/t2i/assets/extra.css">
        <link rel="stylesheet" href="https://objectstorage.global.loongapi.com/loongapiSources/media/bot/t2i/assets/curtain.css">
        <link href="https://objectstorage.global.loongapi.com/loongapiSources/media/bot/t2i/assets/stylesheets/glightbox.min.css" rel="stylesheet">
        <script src="https://objectstorage.global.loongapi.com/loongapiSources/media/bot/t2i/assets/javascripts/glightbox.min.js"></script>
        </head>
        <body dir="ltr" data-md-color-scheme="default" data-md-color-primary="amber" data-md-color-accent="indigo"
        class="vsc-initialized">
        <div class="md-container" data-md-component="container">
            <main class="md-main" data-md-component="main">
            <div class="md-main__inner md-grid">
                <div class="md-content" data-md-component="content">
                <article class="md-content__inner md-typeset">

                    {}
                    
                </article>
                </div>
            </div>
            </main>
            <footer class="md-footer">
            <div class="md-footer-meta md-typeset">
                <div class="md-footer-meta__inner md-grid">
                <div class="md-copyright">

                    <div class="md-copyright__highlight">
                    Copyright © 2016 - 2022 神麟项目团队 &amp; 寒武天机API系统
                    </div>
                </div>

                </div>
            </div>
            </footer>
        </div>
        </body>
        </html>

    """

    async def genHTML(self,mdcontent) -> str:

        content = await asyncio.to_thread(self.markdown,mdcontent)
        html = self.tpl.format(content)
        return html


    async def GetChromeTextFromRemoteServer(
        self,
        content:str,
        session:aiohttp.ClientSession,
        viewport_height:int = 720,
        viewport_width:int= 1080,
        screenshot_quality:int = 90 ,
        format:str = "jpeg"
        ) ->bytes|None:


        htm = await self.genHTML(content)

        data = {
            "content":htm,
            "scale":"device",
            "screenshot_quality":screenshot_quality,
            "viewport_height":viewport_height,
            "viewport_width":viewport_width,
            "wait_until":"load",
            "format":format

        }
        async with session.post("https://v1.loongapi.com/v1/tool/playwright/screenshot/chromium",data= data) as response:
            if response.status == 200:
                return await response.read()
            else:
                return None
    
    async def genWEBuid(self,mdcontent) -> str:
        content = await asyncio.to_thread(self.markdown,mdcontent)
        redis_client = await redis.get_redis_session()
        uid = str(uuid.uuid3(uuid.NAMESPACE_DNS,content))
        async with redis_client.client() as session:
            time = 60 * 60
            await session.setex(name="md2img_" +uid,time=time,value=content)

        return uid



