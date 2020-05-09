"""it is an example ft_unit that implements active replication and is reliable"""

from .ft_unit_base import ReplicationStratergy, FaultDetectionStratergy, VmPlacementPolicy ,FtUnit
from ..replication_mgr import replica_invoker
from termcolor import colored
# from random import choices
import random

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SEED = 42
random.seed(SEED)

class VmPlacement(VmPlacementPolicy):
    '''atleast one backup not on the same host as the primary'''
    def __init__(self, mech_name):
        logger.debug(colored("creating a VmPlacement object", 'blue', 'on_white'))
        super().__init__(mech_name)

    async def place(self, locations, num_primary, replica_ratio) -> list:
        '''choses the locations where to place the primary and backup VMs
        Args:
            locations: a list of intergers representing locations of hosts

        Returns:
            final_placement: a list of locations of primary and replica VMs
                example:[ 
                            {'primary': {'loc': location of primary VM,
                                    'backup': {loc1: num of VMs,
                                               loc2: num of VMs}
                                    }
                            },
                            ...
                        ]
        '''
        random.seed(SEED)
        
        logger.info(colored("placing the VMs", 'blue'))
        final_placement = []
        for primary_vm in range(num_primary):
            chosen = set()
            placement = {'primary': {}}
            loc = random.choices(locations)
            chosen.add(loc[0])
            placement['primary']['loc'] = loc[0]   #this is a list of locations for pimary VMs
            backup_loc = {}
            num_backup = replica_ratio
            for i in range(num_backup):
                loc = random.choices(locations)
                while loc[0] in chosen:
                    loc = random.choices(locations)
                chosen.add(loc[0])
                prev_val = backup_loc.get(loc[0], 0)
                backup_loc[loc[0]] = prev_val + 1

            placement['primary']['backup'] = backup_loc
            final_placement.append(placement)
        
        return final_placement

    async def place_random(self, locations, num_primary, replica_ratio) -> list:
        '''choses the locations where to place the primary and backup VMs
        Args:
            locations: a list of intergers representing locations of hosts

        Returns:
            final_placement: a list of locations of primary and replica VMs
                example:[ 
                            {'primary': {'loc': location of primary VM,
                                    'backup': {loc1: num of VMs,
                                               loc2: num of VMs}
                                    }
                            },
                            ...
                        ]
        '''
        random.seed(SEED)
        
        logger.info(colored("placing the VMs", 'blue'))
        final_placement = []
        for primary_vm in range(num_primary):
            placement = {'primary': {}}
            loc = random.choices(locations)
            placement['primary']['loc'] = loc[0]   #this is a list of locations for pimary VMs
            backup_loc = {}
            num_backup = replica_ratio
            for i in range(num_backup):
                loc = random.choices(locations)
                prev_val = backup_loc.get(loc[0], 0)
                backup_loc[loc[0]] = prev_val + 1

            placement['primary']['backup'] = backup_loc
            final_placement.append(placement)
        
        return final_placement

class ActiveReplication(ReplicationStratergy):
    """extends the ReplicationStratergy class inherited from base
    implements active replication stratergy using two backups for each primary

    """
    def __init__(self, mech_name, data):
        logger.debug(colored(f"passing data: {data} to Base", 'blue', 'on_white'))
        logging.debug(colored("creating a ActiveReplication object", 'blue', 'on_white'))
        data = {'latency': 'low',
                'availability': 'high',
                'bandwidth': 'moderate',
                'comp_req': 'low'}

        super().__init__("actve_replication", data)

        self.replica_ratio = 3

    async def synchronizer(self, ftm , message):
        '''we are using active replication here'''
        logger.debug(colored(f"msg received by replication stratergy", 'blue', 'on_white'))
        #forward msg to all, wait till majority reponse
        #send ack after mjority resp
        #call synchronizer to continue replication on other nodes
        logger.info(colored(f"using active replication, sending message to all the replicas", 'blue'))
        for vm_id in ftm.all_VMs.keys():
            logger.info(colored(f"sending to vm id[{vm_id}]", 'yellow'))
            await ftm.msg_monitor.send_json(message, 'cloud')

    def populate(self, requirements):
        '''
        Args:
            requirements: {"vms": [
                                    {"num_of_instances": "num",
                                    "config": {"mips": "1000",
                                            "pes": "4",
                                            "ram": "1000",
                                            "bandwidth": "1000",
                                            "size": "10000",
                                            "location": "1"}
                                            }
                                    ],
                            "latency": "low",
                            "availability": "high",
                            "bandwidth": "moderate"
                            }
        '''
        count = 0
        replica_count = 1
        for vm in requirements['vms']:
            count += vm['num_of_instances']
            # replica_count += self.replica_ratio *  
        self.num_of_primary = count
        # self.num_of_primary = len(requirements['vms'])
        self.num_of_replica = self.num_of_primary * self.replica_ratio
        self.primary_config = requirements['vms']
        self.backup_config = requirements['vms']

class FaultDetection(FaultDetectionStratergy):
    """extends the FaultDetectionStratergy base class
    using heartbeat protocol
    """
    def __init__(self, mech_name):
        logger.debug(colored("creating a FaultDetection object", 'blue', 'on_white'))
        data = {}
        super().__init__(mech_name, data)
        
    async def detection_strat(self):
        ''''implement the heartbear protocol'''
        #possibly accept status from resource manager and evaluate it

class ReliableFtUnit(FtUnit):
    """extends the FtUnit base class"""
    def __init__(self, id, replication_strat, detection_strat, vm_placement):
        logger.debug(colored("creating a ReliableFtUnit object", 'blue', 'on_white'))
        super().__init__(id, replication_strat, detection_strat, vm_placement)
    
    def populate(self, requirements):
        logger.debug(f"populating the ft_unit: {self.id}")
        self.replication_strat.populate(requirements)

def create_ft_unit():
    logging.debug(colored("create_ft_unit called", 'blue', 'on_white'))
    vm_placement = VmPlacement("backup_host != primary_host")
    logger.debug(colored("calling ActiveReplication", 'blue', 'on_white'))
    data = {'test': 'data'}
    repl_strat = ActiveReplication('active_replication', data)
    fault_det = FaultDetection('heartbeat')
    ft_unit = ReliableFtUnit("demo_ft_unit", repl_strat, fault_det, vm_placement)

    logger.debug(colored("ft_unit created", 'blue', 'on_white'))
    return ft_unit