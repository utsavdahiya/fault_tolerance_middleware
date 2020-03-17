'''
module that handles all communicaiton

its purpose is to route and buffer messages
it performs two functions:
	>an interface for communication bw all the composition
	>it also acts as interface bw the ftm and cloudsim
'''
import asyncio
import aiohttp
from aiohttp import web
import nest_asyncio
nest_asyncio.apply()

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

	async def connect_cloud(self):
		logger.info("connecting to cloud...")
		async with aiohttp.ClientSession() as session:
			self.cloud_session = session
			async with session.get(self.cloudsim_url, data=b'hentai') as resp:
				data = await resp.text()
				logger.info("connected succcessfully")
				logger.info("connection response: " + data)

	def disconnect(self):
		pass

	async def send(self, msg, destination):
		logger.info("sending msg to " + str(destination))
		if(destination == 'cloud'):
			url = self.cloudsim_url
			async with self.cloud_session as session:
			   async with session.post(url, json = msg) as resp:
				   data = await resp.text()
				   logger.info("answer: " + data)
		else:
			pass

	async def cloud_get_handler(self, request):
		return web.Response(text="Controooool Uday!!")

	async def cloud_post_handler(self, request):
		logger.info("post req received at /post")
		return web.Response(text="you posted successfully")

	async def websocket_handler(self, request):
		ws = web.WebSocketResponse()
		await ws.prepare(request)
		await ws.send_str("welcome to websocket server")
		async for msg in ws:
			logger.info("recvd msg: " + str(msg.data))
			if msg.type == aiohttp.WSMsgType.TEXT:
				if msg.data == 'close':
					await ws.close()
				else:
					await ws.send_str(msg.data + '/server_resp')
					logger.info("sent reply to ws")
			elif msg.type == aiohttp.WSMsgType.ERROR:
				print('ws connection closed with exception %s' %ws.exception())

		print('websocket connection closed')

		return ws

	async def server_setup(self, port):
		'''server for cloudsim'''
		app = web.Application()
		app.add_routes([web.get('/ws', self.websocket_handler),
                    web.get('/', self.cloud_get_handler),
                    web.post('/post', self.cloud_post_handler)])
		logger.info("application running")
		web.run_app(app, port = port)