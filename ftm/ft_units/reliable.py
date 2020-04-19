"""it is an example ft_unit that implements active replication and is reliable"""

from .ft_unit_base import ReplicationStratergy, FaultDetectionStratergy, FtUnit

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActiveReplication(ReplicationStratergy):
    """extends the ReplicationStratergy class inherited from base
    implements active replication stratergy using two backups for each primary

    """
    def __init__(self, mech_name):
        data = {'latency': 'low',
                'availability': 'high',
                'comp_req': 'low'}
        super().__init__("actve_replication", data)

    def replication_strat(self, primary, backups):
        pass

    def populate(self, requirements):
        pass

class FaultDetection(FaultDetectionStratergy):
    """extends the FaultDetectionStratergy base class
    using heartbeat protocol
    """
    def __init__(self, mech_name, data):
        super().__init__(mech_name, data)

class ReliableFtUnit(FtUnit):
    """extends the FtUnit base class"""
    def __init__(self, id, replication_strat, detection_strat):
        super().__init__(id, replication_strat, detection_strat)
    
    def populate(self, requirements):
        self.replication_strat.populate(requirements)

def create_ft_unit():
    repl_strat = ActiveReplication()
    fault_det = FaultDetection()
    ft_unit = ReliableFtUnit("demo_ft_unit", repl_strat, fault_det)