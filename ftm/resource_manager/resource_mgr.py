'''manages and monitors the resources of the cloud infrastructure provider'''
import asyncio

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResouceManager:
    def __init__(self, msg_monitor: MessageMonitor):
        self.msg_monitor = msg_monitor  #messaging monitor allows RM to communicate with cloudsim
        self.VMs = []   #a list of VMs
        self.timer = 10 #timer for monitoring schelduling

    async def monitor(self):
        #monitor the VMs to check if they are running smoothly
        while True:
            asyncio.sleep(self.timer)   #check every "timer" seconds
            for vm in self.VMs:
                #check vm status with cloudsim
                pass

    async def instantiate(self, vm: VM) -> (int, int):
        '''instantiate the given VM 
        
            Args:
                vm: it is an instance of VM() defined in replication manager package
            Return:
                returns the VM config id and an SUCCESS/ERROR CODE- (1: success, 0:failure)
                #error codes can be made more descriptive in future
        '''
        #add the VM to self.VMs
        #send req to cloudsim to instantiate the required VM config
        pass