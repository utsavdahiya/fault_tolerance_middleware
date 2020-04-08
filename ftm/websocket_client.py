import asyncio
import aiohttp

class FtmClient():
    def __init__(self, id: str):
        self.id = id

    async def connect(self, url:str):
        async with aiohttp.ClientSession().ws_connect(url) as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close cmd':
                        await ws.close()
                        break
                    else:
                        await ws.send_str('my requirements')
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
async def main():
    client = FtmClient("crime master gogo")
    client.connect("http://0.0.0.0:8082")