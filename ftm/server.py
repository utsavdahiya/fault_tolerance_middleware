import ftm_kernel.service_dir
import ft_units
import ft_units.base
from messaging_monitor import MessagingMonitor
import json
import asyncio

import nest_asyncio
nest_asyncio.apply()

import logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class Application():
    def __init__(self, msg_monitor):
        self.msg_monitor = msg_monitor

    def on_connect_client(self, data):
        """callback on establishing contact with client"""
        logger.info("App connected: {}".format(data))

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
    port = "8081"   #set port number to where you want to send requests
    tasks.append(asyncio.create_task(app.msg_monitor.server_setup(port)))
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
    tasks.append(asyncio.create_task(app.msg_monitor.client_setup(8082)))   #starting server where client can connect to

    #gathering all the tasks
    await asyncio.gather(task for task in tasks)

if __name__=='__main__':
   asyncio.run(main())