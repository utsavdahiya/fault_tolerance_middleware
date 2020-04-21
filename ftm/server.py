import ftm_kernel.service_dir
import ftm_middleware
import ft_units
from messaging_monitor import MessagingMonitor
import json
import asyncio
from termcolor import colored

import nest_asyncio
nest_asyncio.apply()

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

NUM_LOCATIONS = 10

class Client:
    counter = 0
    def  __init__(self, websocket):
        Client.counter += 1
        self.id = str(Client.counter)
        self.websocket = websocket
        self.ftm_list = []

class Application():
    def __init__(self, msg_monitor):
        self.msg_monitor = msg_monitor
        self.clients = []
        self.client_dict = {}   #dict: <client_websocket, client_obj>
        self.ftm_dict = {}   #dict: <client_id, ftm>
        self.ftm_list = []
        self.locations = [i for i in range(NUM_LOCATIONS)]

    async def on_connect_client(self, data: dict):
        """callback on establishing contact with client

            Args:
                data: a dictionary of data items
                    example- {'websocket': websocket session for the client} 
        """

        logger.info(colored("new client connected", 'green'))
        if 'websocket' not in data.keys():
            raise("websocket session object not passed on new client connection")
        #create a new client instance for the newly connected client
        client = Client(data['websocket'])
        #register client with app
        self.clients.append(client)
        logger.info(colored("registered client with app", 'green'))
        self.client_dict[data['websocket']] = client
        return client.id

    async def on_requirements(self, data: dict):
        '''start procedure after receiving requirments
        
        Args:
            data: client related info 
                    example: {"websocket": websocket_endpoint_of client
                            "client_id": id_of_client
                            "client_req":{"vms": [{"num_of_instances": "num",
                                                    "config": {"mips": "1000",
                                                            "pes": "4",
                                                            "ram": "1000",
                                                            "bandwidth": "1000",
                                                            "size": "10000",
                                                            "location": "1"}
                                                }],
                                        "latency": "low",
                                        "availability": "high",
                                        "bandwidth": "moderate"
                                    }
                            }
        '''
        #start an FTM instance for the client
        logger.info(colored(f"client requirements received", 'green'))
        client_id = data['client_id']
        info = {}
        info['client_req'] = data['client_req']
        info['locations'] = self.locations
        ftm_instance = await ftm_middleware.start_ftm(self, client_id, self.msg_monitor, info)
        #register this ftm instance with the application
        self.ftm_dict[client_id] = ftm_instance
        self.ftm_list.append(ftm_instance)
                
        logger.info(colored("ftm_created for the client", 'green'))
        #return list of VMs to the client
        list_primary = []
        for vm_obj in ftm_instance.VMs:
            vm_id = [*vm_obj]
            vm_id = vm_id[0]
            list_primary.append(vm_id)
        # list_primary = [*vm_id for vm_id in ftm_instance.VMs]
        # list_primary = [ftm_instance.all_VMs[vm_id] for vm_id in list_primary]
        msg = {'desc': 'VMs',
                'list': list_primary}
        logger.debug(colored(f"sending vm list to client", 'green', 'on_white'))
        await self.msg_monitor.send_json(msg, client_id)
        
        #starting the resource manager monitor
        asyncio.create_task(ftm_instance.resource_mgr.monitor(ftm_instance))

    async def on_location(self, data):
        '''
            data = {'client_ws': client_ws,
                    'locations': [locations]}
        '''
        logger.debug(colored(f"on_location hit", 'blue', 'on_white'))
        # client = self.client_dict[data['client_ws']]
        locations = data['locations']
        ftm_instance = self.ftm_list[0]
        await ftm_middleware.cont_ftm(ftm_instance, locations)
        
    async def on_status(self, data):
        logger.debug(colored(f"on_status hit", 'blue', 'on_white'))
        client_id = data.get('client_id', None)
        if client_id is None:
            raise Exception(colored(f"client_id was not present in status message", 'red'))
        ftm_instance = self.ftm_dict[client_id]
        ftm_instance._queue.put({'action': 'STATUS', 'data': data})

    async def on_cloudlet(self, data):
        client_id = data['client_id']
        msg = data['instantiate_cloudlet']
        #send this message to ftm 
        ftm = self.ftm_dict[client_id]
        logger.info(colored(f"calling synchronizer to process the message", 'blue'))
        await ftm.ft_unit.replication_strat.synchronizer(ftm, msg)

    async def on_connect_cloud(self, data):
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
    #registering callbaks with msg_monitor
    app.msg_monitor.callbacks['on_connect_cloud'] = app.on_connect_cloud
    app.msg_monitor.callbacks['on_connect_client'] = app.on_connect_client
    app.msg_monitor.callbacks['on_requirements'] = app.on_requirements
    app.msg_monitor.callbacks['on_cloudlet'] = app.on_cloudlet
    app.msg_monitor.callbacks['on_status'] = app.on_status

    #initialising server where you can send requests
    cloud_side_port = "8081"   #set port number to where you want to send requests
    tasks.append(asyncio.create_task(app.msg_monitor.cloud_setup(cloud_side_port)))
    '''my server is now running and can handle your requests at:
        get_req: /
        post_rep: /post
        websocket messages: /ws'''

    # tasks.append(asyncio.create_task(app.msg_monitor.connect_cloud())) #sends a simple get req to your server
    msg = {"desc": "hum honge kamiyaaab"}   #msg has to be in json format
    msg = json.dumps(msg)   #converts it to json
    logger.info("sending msg")
    # tasks.append(asyncio.create_task(app.msg_monitor.send(msg, 'cloud'))) #it is a post req, cloud is the destination and is automatically set to cloudsim_url you provide above

    #starting client websocket server
    # app['client_websockets'] = {}   #dict to store client sessions
    client_side_port = '8082'   #port where clients would connect
    tasks.append(asyncio.create_task(app.msg_monitor.client_setup(client_side_port)))   #starting server where client can connect to

    # tasks.append(asyncio.create_task(app.msg_monitor.test_server()))
    #gathering all the tasks
    # await asyncio.gather(task for task in tasks)
    await asyncio.gather(*tasks)

if __name__=='__main__':
   asyncio.run(main())