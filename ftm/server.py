import ftm_kernel.service_dir
import ftm_middleware
import ft_units
from messaging_monitor import MessagingMonitor
import json
import asyncio

import nest_asyncio
nest_asyncio.apply()

import logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class Client:
    counter = 0
    def  __init__(self, websocket):
        Client.counter += 1
        self.id = Client.counter
        self.websocket = websocket
        self.ftm_list = []

class Application():
    def __init__(self, msg_monitor):
        self.msg_monitor = msg_monitor
        self.clients = []

    def on_connect_client(self, data: dict):
        """callback on establishing contact with client

            Args:
                data: a dictionary of data items
                    example- {'websocket': websocket session for the client} 
        """

        logger.info("client connected: {}".format(data))
        if 'websocket' not in data.keys():
            raise("websocket session object not passed on new client connection")
        #create a new client instance for the newly connected client
        client = Client(data['websocket'])
        #register client with app
        self.clients.append(client)


    async def on_requirements(self, data: dict):
        #start an FTM instance for the client
        # ftm = ftm_middleware.FTM(self)
        #register this ftm instance with the application
        #call start_ftm here
        pass

    def on_connect_cloud(self):
        pass

    def on_client_msg(self):
        pass

    def on_cloud_msg(self):
        pass

async def main():
    tasks = []  #list of tasks to be run concurrently

    # unit = ft_units.base.FtUnit("007", "replication", "fault_tolerance")
    # unit.demo()
    cloudsim_url = 'http://0.0.0.0:8080/'   #set this to the url where your server is running
    msg_monitor = MessagingMonitor(cloudsim_url)
    app = Application(msg_monitor)

    #initialising server where you can send requests
    cloud_side_port = "8081"   #set port number to where you want to send requests
    tasks.append(asyncio.create_task(app.msg_monitor.server_setup(cloud_side_port)))
    '''my server is now running and can handle your requests at:
        get_req: /
        post_rep: /post
        websocket messages: /ws'''

    tasks.append(asyncio.create_task(app.msg_monitor.connect_cloud())) #sends a simple get req to your server
    msg = {"desc": "hum honge kamiyaaab"}   #msg has to be in json format
    msg = json.dumps(msg)   #converts it to json
    logger.info("sending msg")
    tasks.append(asyncio.create_task(app.msg_monitor.send(msg, 'cloud'))) #it is a post req, cloud is the destination and is automatically set to cloudsim_url you provide above

    #starting client websocket server
    app['client_websockets'] = {}   #dict to store client sessions
    client_side_port = '8082'   #port where clients would connect
    tasks.append(asyncio.create_task(app.msg_monitor.client_setup(client_side_port)))   #starting server where client can connect to

    #gathering all the tasks
    await asyncio.gather(task for task in tasks)

if __name__=='__main__':
   asyncio.run(main())