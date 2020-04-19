"""it is an example ft_unit that implements active replication and is reliable"""

from .ft_unit_base import ReplicationStratergy, FaultDetectionStratergy, VmPlacementPolicy ,FtUnit
from replication_mgr import replica_invoker

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VmPlacement(VmPlacementPolicy):
    '''atleast one backup not on the same host as the primary'''
    def __init__(self):
        super().__init__()

    async def place(self, locations, num_primary, num_backup):
        #chosing loc 1 for primary and subsequent for backups
        placement = {}
        placement['primary'] = [locations[0]]   #this is a list of locations for pimary VMs
        backup_loc = {}
        for i in range(1, len(locations)):
            vm_loc = backup_loc.get(locations[i], 0)
            backup_loc[locations[i]] += 1

        placement['backup'] = backup_loc
        
        return placement

class ActiveReplication(ReplicationStratergy):
    """extends the ReplicationStratergy class inherited from base
    implements active replication stratergy using two backups for each primary

    """
    def __init__(self, mech_name):
        data = {'latency': 'low',
                'availability': 'high',
                'comp_req': 'low'}
        super().__init__("actve_replication", data)

        self.replica_ratio = 2

    async def replication_strat(self, message):
        '''we are using active replication here'''
        logger.info(f"msg received by replication stratergy")
        #forward msg to all, wait till majority reponse
        #send ack after mjority resp
        #call synchronizer to continue replication on other nodes

    def populate(self, requirements):
        self.num_of_primary = len(requirements['vms'])
        self.num_of_replica = self.num_of_primary * self.replica_ratio
        self.primary_config = requirements['vms']
        self.backup_config = requirements['vms'][0]

class FaultDetection(FaultDetectionStratergy):
    """extends the FaultDetectionStratergy base class
    using heartbeat protocol
    """
    def __init__(self, mech_name):
        data = {}
        super().__init__(mech_name, data)
        
    async def detection_strat(self):
        ''''implement the heartbear protocol'''
        #possibly accept status from resource manager and evaluate it

class ReliableFtUnit(FtUnit):
    """extends the FtUnit base class"""
    def __init__(self, id, replication_strat, detection_strat):
        super().__init__(id, replication_strat, detection_strat)
    
    def populate(self, requirements):
        logger.info(f"populating the ft_unit: {self.id}")
        self.replication_strat.populate(requirements)

def create_ft_unit():
    repl_strat = ActiveReplication('active_replication')
    fault_det = FaultDetection('heartbeat')
    ft_unit = ReliableFtUnit("demo_ft_unit", repl_strat, fault_det)

    return ft_unit