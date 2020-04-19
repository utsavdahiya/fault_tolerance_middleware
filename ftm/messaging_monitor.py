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
import json
from termcolor import colored
# import nest_asyncio
# nest_asyncio.apply()

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessagingMonitor():

	def __init__(self, cloudsim_url):
		self.callbacks = {}	# a dict of callback functions
		
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

	async def disconnect(self):
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

	async def send_str(self, msg, dest):
		'''Args:
			dest: client_id'''
		if(dest == 'cloud'):
			#send msg to cloud
			ws = self.cloud_session
			await ws.send_str(msg)
		if dest not in self.session.keys():
			raise(colored(f"client: {dest} was not found", 'red'))
		else:
			ws = self.session[dest]
			await ws.send_json(msg)
        #now call replica invoker to invoke at specified loacations

	async def send_json(self, msg, dest):
		'''Args:
			dest: client_id'''
		if(dest == 'cloud'):
			#send msg to cloud
			ws = self.cloud_session
			await ws.send_json(msg)
			if(msg['desc'] == "get_location"):
				resp = await ws.receive_json()
				logger.info(colored("recvd msg: " + str(msg.data), 'yellow'))
				return resp
		if dest not in self.session.keys():
			raise(colored(f"client: {dest} was not found", 'red'))
		else:
			ws = self.session[dest]
			await ws.send_json(msg)
        #now call replica invoker to invoke at specified loacations
        
	async def cloud_get_handler(self, request):
		logger.info("get req received")
		return web.Response(text="Controooool Uday!!")

	async def cloud_post_handler(self, request):
		logger.info("post req received at /post")
		return web.Response(text="you posted successfully")

	async def client_websocket_handler(self, request):
		ws = web.WebSocketResponse()
		await ws.prepare(request)
		await ws.send_str("Welcome to FTM, send your requirements")
		data = {}
		data['websocket'] = ws
		#hitting callback for when a new client connects
        #now call replica invoker to invoke at specified loacations
        
		client_id = await self.callbacks['on_connect_client'](data)
		self.session[client_id] = ws
		data['client_id'] = client_id
		async for msg in ws:
			logger.info(f"client msg: {str(msg.data)}")
			if msg.type == aiohttp.WSMsgType.TEXT:
				if msg.data == 'close':
					logger.info("closing the client side server")
					await ws.close()
				else:
					try:
						client_req = json.loads(msg.data)
						data['client_req'] = client_req
						logger.info(f"client requirements received: {data}")
						await self.callbacks['on_requirements'](data)
						#send VM started reponse
					except:
							await ws.send_str(f"{msg.data}/server_resp")
			elif msg.type == aiohttp.WSMsgType.ERROR:
				print('ws connection closed with exception %s' %ws.exception())
		
		logger.info(colored("ws client connection closed", 'red'))

	async def client_get(self, request):
		logger.info(f"client get req received")
		return web.Response(text="hello client")

	async def cloud_websocket_handler(self, request):
		logger.info(colored("cloud handler approached", 'yellow'))
		ws = web.WebSocketResponse()
		await ws.prepare(request)
		msg = {"desc": "welcome message"}
		await ws.send_json(msg)
		self.cloud_session = ws
		async for msg in ws:
			logger.info(colored("recvd msg: " + str(msg.data), 'yellow'))
			if msg.type == aiohttp.WSMsgType.TEXT:
				if msg.data == 'close':
					await ws.close()
				else:
					try:
						recvd_msg = json.loads(msg.data)
						if recvd_msg['desc'] == '':
							pass
					except:
						# await ws.send_str(msg.data + '/server_resp'+'\n')
						# logger.info("sent reply to ws")
						logger.info(colored(f"msg recvd: {msg.data}", 'yellow'))
			elif msg.type == aiohttp.WSMsgType.ERROR:
				print('ws connection closed with exception %s' %ws.exception())

		logger.info(colored('cloud websocket connection closed', 'red'))

	async def cloud_setup(self, port: int):
		'''server for cloudsim'''
		server_app = web.Application()
		server_app.add_routes([web.get('/ws', self.cloud_websocket_handler),
                    web.get('/', self.cloud_get_handler),
                    web.post('/post', self.cloud_post_handler)])
		logger.info(colored(f"cloud_server starting at {port}", 'yellow'))
		web.run_app(server_app, port = port)
		logger.info("-----------------does this line ever print??------------")

	async def client_setup(self, port: int):
		'''server for the client to connect to'''
		logger.info(f"req to start client server at {port}")
		client_app = web.Application()
		client_app.add_routes([web.get('/ws', self.client_websocket_handler),
							web.get('/', self.client_get)])
		logger.info(f"client_server starting at {port}")
		web.run_app(client_app, port = port)

	async def get_handler(self, request):
		print(f"request received")
		return web.Response(text="test server landing page")

	async def test_server(self):
		logger.info(f"inside test_server")
		app = web.Application()
		app.add_routes([web.get('/', self.get_handler)])
		web.run_app(app)