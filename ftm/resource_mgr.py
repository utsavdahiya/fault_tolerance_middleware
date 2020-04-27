'''manages and monitors the resources of the cloud infrastructure provider'''
import json
import asyncio
from termcolor import colored

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ResouceManager:
    def __init__(self, msg_monitor):
        logger.debug(colored("creating ResourceManger object", 'blue', 'on_white'))
        self.msg_monitor = msg_monitor  #messaging monitor allows RM to communicate with cloudsim
        self.VMs = {}   #a dict of VMs
        self.timer = 2 #timer for monitoring schelduling
        self.monitor_list = []
        
    async def evaluate(self, vm_status):
        '''vm_status = {"desc": "vm_status_reply"
                        "allocated_bandwidth":"10000", 
                        "available_bandwidth":"10000",
                        "capacity_bandwidth":"20000",
                        "current_requested_bandwidth":"20000",
                        "cpu_percent_utilization":"80",
                        "current_requested_total_mips":"500",
                        "allocated_ram":"4096",
                        "available_ram":"8192",
                        "capacity_ram":"8192",
                        "current_requested_ram":"8192",
                        "allocated_storage":"12800",
                        "available_storage":"25600",
                        "capacity_storage":"25600",
                        "condition":"working"
                    }
                    '''
        if vm_status['condition'] != "working":
            logger.info(colored(f"vm [{id}] condition is not working!!", 'red'))
            pass
        elif vm_status['cpu_percent_utilization'] > 95:
            pass
        elif vm_status['allocated_ram']/vm_status['capacity_ram'] > 90:
            pass
    
    async def monitor(self, ftm):
        #monitor the VMs to check if they are running smoothly
        logger.debug(colored(f"monitoring the VMs for status"))
        while True:
            await asyncio.sleep(self.timer)   #check every "timer" seconds
            for vm_id in self.monitor_list:
                #check vm status with cloudsim
                msg = {"desc": "status",
                    "id": vm_id,
                    "client_id": ftm.client_id
                }
                logger.info(colored("checking status", 'blue'))
                await self.msg_monitor.send_json(msg, 'cloud')

    async def instantiate(self, ftm, vm) -> (str, int):
        '''instantiate the given VM 
        
            Args:
                ftm: the ftm instance for which vm is to be instantiated
                vm: it is an instance of VM() defined in replication manager package
            Return:
                returns the VM id and an SUCCESS/ERROR CODE- (1: success, 0:failure)
                #error codes can be made more descriptive in future
        '''
        logger.debug(colored(f"invoking replica {vm.id}", 'blue', 'on_white'))
        #register vm with the resource manager
        self.VMs[vm.id] = vm
        #send req to cloudsim to instantiate the required VM config
        # msg = vm.config
        msg = {"desc": "instantiate_vm",
                "client_id": ftm.client_id,
                "VM": [vm.config],
            }
        #adding id to vm:
        msg['VM'][0]['vm_id'] = vm.id
        logger.debug(colored(f"calling cloud to allocate VM", 'blue', 'on_white'))
        await self.msg_monitor.send_json(msg, 'cloud')

        #if successful:
        # self.VMs[vm.id].status = 'active'
        # logger.debug(colored(f"vm: {vm.id} activated", 'blue', 'on_white'))
        code = 'SUCCESS'
        return vm.id, code
    
    async def terminate(self, vm) -> (str, str):
        '''terminate the specified VM 

            Args:
            vm: an instance of VM()
            Returns:
                returns the id of the VM along with a STATUS CODE of the operation
                    SUCCESS
                    FAILURE
        '''
        if vm not in self.VMs:
            raise("invalid VM given to terminate")
        #send request to cloudsim to terminate the given VM
        #update the VMs list
        self.VMs.remove(vm)