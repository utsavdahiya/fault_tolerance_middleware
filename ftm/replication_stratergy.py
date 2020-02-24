'''
    defines the functions required to implement a replication stratergy
'''

class Replication_stratergy:
    """base class for replication stratergy"""

    def __init__(self):
        self.mechanism = "active/passive/semi-active"   #placeholder for actual mechanism implementaion object
        self.num_of_replica = 0
        self.backup_config = [] #a list of configurations(YAML file) for backup VMs
    
    def replicationStrat(self):
        raise NotImplementedError()