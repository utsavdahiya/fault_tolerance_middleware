import asyncio
import aiohttp
import json
from termcolor import colored
import multiprocessing
import sys

from . import globals

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("__name__")

messages = {
    'instantiate_cloudlet': {
                    "desc":"instantiate_cloudlet",
                    "vm_id": "id of vm",
                    "cloudlet":[]
                },
    'cloudlet': {
                    "file_size":"1024",
                    "output_size":"1024",
                    "pes":"2",
                    "length":"10000"
                }
}

class FtmClient():
    def __init__(self, id: str):
        self.id = id
        self.ws = None
        self.basic_config = None
        self.VMs = None
        self.first_time = True

    async def on_vm_creation(self, data):
        logger.info(colored(f"VMs created successfully", 'green'))
        logger.info(colored(f"vm details: {json.dumps(data, indent=2)}", 'blue'))

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
                        if self.first_time: #this will run only once
                            self.first_time = False
                            try:
                                with open("ftm/client_req.json") as f:
                                    logger.info(colored("file loaded:", on_color='on_green'))
                                    # print(f)
                                    data = json.load(f)
                            except Exception as e:
                                logger.info(colored(f"error: {e}", 'red'))
                            self.basic_config = data
                            logger.info(f"sending client requirements: {data}")
                            await ws.send_json(data)
                            # pause = input("waiting for server ftm instantiaion")
                            logger.info(colored(f"waiting for ftm instantiation..."))
                        else:
                            try:
                                recvd_msg = json.loads(msg.data)
                                if recvd_msg['desc'] == 'VMs':
                                    await self.on_vm_creation(recvd_msg)
                                else:
                                    logger.info(colored("json received", 'green'))
                            except:
                                logger.info(colored("msg format not JSON", 'red'))
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
            logger.info(f"closed connection to url:{url}")
            await ws.close()

    async def send_json(self, msg):
        '''send message to ftm'''
        logger.debug(colored(f"sending msg: {json.dumps(msg, indent=2)}", 'green', 'on_white'))
        ws = self.ws
        await ws.send_json(msg)
        
    async def send_str(self, msg):
        '''send string message to ftm'''
        ws = self.ws
        await ws.send_str(msg)

    async def vm_update(self):
        for parameter in self.basic_config:
            self.basic_config[parameter] *= 1.5

async def main(queue):
    client = FtmClient("Hachiko")
    port = globals.PORT_CLIENT
    asyncio.create_task(client.connect(f"http://0.0.0.0:{port}/ws"))
    await asyncio.sleep(5)
    # cont = input("start an application on the VM?")

    # logger.info(colored("starting a application on the VM", 'green'))
    # msg = messages['instantiate_cloudlet']
    # msg['cloudlet'] = [messages['cloudlet']]
    # await client.send_json(msg)

    # cont = input("waiting for ftm")
    print("waiting for ftm")
    resp = queue.get()
    print(f"received: {resp} | Now quitting")
    sys.exit()

def run_main(queue):
    asyncio.run(main(queue))