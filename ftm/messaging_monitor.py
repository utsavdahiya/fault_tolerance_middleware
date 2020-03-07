'''
module that handles all communicaiton

its purpose is to route and buffer messages
it performs two functions:
    >an interface for communication bw all the composition
    >it also acts as interface bw the ftm and cloudsim
'''
import asyncio
import aiohttp

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessagingMonitor():

    def __init__(self, cloudsim_url):
        self.queue = []     #as a buffer for incoming messages
        self.tasks = []     #a list of functions

        self.cloudsim_url = cloudsim_url
        self.cloud_session = "session_obj"
        self.session = {}   #a dictionary of <client_id:client_session>

    async def connect(self):
        async with aiohttp.ClientSession() as session:
            self.cloud_session = session

    def disconnect(self):
        pass

    async def send(self, msg, destination):
       if(destination == "cloud"):
           url = self.cloudsim_url
           async with self.cloud_session as session:
               async with session.post(url, json = msg)
        else:
            logger.info("non-cloud msg")

    async def handler(request):
        return web.Response(text="Ohaaio senpaii")

    async def server(self):
        '''server for cloudsim'''
        pass