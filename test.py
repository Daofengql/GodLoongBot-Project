import asyncio

import aiohttp

chunksize = 16384

async def main():
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get("https://speed.hetzner.de/1GB.bin") as r:
            size = 0
            async for chunk in r.content.iter_chunked(chunksize):
                if len(chunk) == chunksize:
                    size += chunksize
                else:
                    size += len(chunk)
    print(size/1024/1024/1024)
            


asyncio.run(main())