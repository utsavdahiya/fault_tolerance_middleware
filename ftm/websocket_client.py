import asyncio
import aiohttp
import json
from termcolor import colored

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("__name__")

class FtmClient():
    def __init__(self, id: str):
        self.id = id
        self.ws = None
        self.basic_config = None

    async def connect(self, url:str):
        logger.info(f"connecting to ftm at {url}")
        async with aiohttp.ClientSession().ws_connect(url) as ws:
            self.ws = ws    #storing the web socket session
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close cmd':
                        logger.info(f"closing connection to url:{url}")
                        await ws.close()
                        break
                    else:
                        logger.info(f"received msg: {msg.data}")
                        with open('client_req.json') as f:
                            logger.info("file loaded:")
                            # print(f)
                            data = json.load(f)
                            self.basic_config = data
                            logger.info(f"sending client requirements: {data}")
                        await ws.send_json(data)
                        pause = input("waiting for server ftm instantiaion")
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
            logger.info(f"closed connection to url:{url}")
            await ws.close()

    async def send_json(self, msg):
        '''send message to ftm'''
        ws = self.ws
        ws.send_json(msg)
        
    async def send_str(self, msg):
        '''send string message to ftm'''
        ws = self.ws
        ws.send_str(msg)

    async def vm_update(self):
        for parameter in self.basic_config:
            self.basic_config[parameter] *= 1.5

async def main():
    client = FtmClient("Hachiko")
    await client.connect("http://0.0.0.0:8082/ws")

    logger.info(colored("starting a application on the VM", 'green'))
    await client.vm_update()
    
asyncio.run(main())