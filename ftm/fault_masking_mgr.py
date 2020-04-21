import asyncio
import json
from termcolor import colored

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class FaultMasking:
    def __init__(self, mech_name):
        logger.debug(colored("creating a FaultMasking object", 'blue', 'on_white'))
        self.mech_name = mech_name

    async def handle_fault(self, data):
        ftm = data['ftm']
        vm_id = data['vm_id']
        #change vm status to inactive
        ftm.all_VMs[vm_id].status = 'inactive'
        #migrating the vm
        msg = {
                "desc": "migration",
                "id": vm_id
            }
        logger.info(colored(f"migrating faulty VM [{vm_id}]", 'red'))
        await ftm.msg_monitor.send_json(msg, 'cloud')
        logger.info(colored(f"vm id[{vm_id}] has been successfully migrated to another host", 'green', 'on_white'))