import ftm_kernel.service_dir
import ft_units
import ft_units.base
from messaging_monitor import MessagingMonitor
import json

import logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class Application():
    def __init__(self, msg_monitor):
        self.msg_monitor = msg_monitor

    def on_connect_client(self):
        """callback on establishing contact with client"""
        pass

    def on_connect_cloud(self):
        pass

    def on_client_msg(self):
        pass

    def on_cloud_msg(self):
        pass

def main():
    # unit = ft_units.base.FtUnit("007", "replication", "fault_tolerance")
    # unit.demo()
    cloudsim_url = 'http://0.0.0.0:8080/'   #set this to the url where your server is running
    msg_monitor = MessagingMonitor(cloudsim_url)
    app = Application(msg_monitor)

    #initialising server where you can send requests
    port = "8081"   #set port number to where you want to send requests
    app.msg_monitor.server_setup(port)
    '''my server is now running and can handle your requests at:
        get_req: /
        post_rep: /post
        websocket messages: /ws'''

    app.msg_monitor.connect_cloud() #sends a simple get req to your server
    msg = {"desc": "hum honge kamiyaaab"}   #msg has to be in json format
    msg = json.dumps(msg)   #converts it to json
    app.msg_monitor.send(msg, 'cloud')  #cloud is the destination and is automatically set to cloudsim_url you provide above
    


if __name__=='__main__':
   main()