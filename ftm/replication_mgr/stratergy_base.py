'''This provides a template for creatiung replication stratergies'''

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReplicationStratergy:
    """base class for replication stratergy"""

    def __init__(self, mech_name, data):
        """initialises variables
        
            mech_name:str- the name/id of the chosen mechanism
            data:<key:value>- dict(hashmap) of required paramters for the strat. 
                        eg- {num_of_replica:5, primary_config:<config>, backup_config:<config>}
        """
        self.mech_name = mech_name   #type:str- placeholder for actual mechanism implementaion object
        self.num_of_primary = data.get('num_of_primary', None)
        if not self.num_of_primary:
            raise("Number of primary VMs are must")
        self.num_of_replica = data.get('num_of_replica', None)
        if not self.num_of_replica:
            self.num_of_replica = max(self.num_of_primary, 1)   #atleast one replica if nothing specified
        self.backup_config = data.get('backup_config', None) #a list of configurations(YAML file) for backup VMs
        if not self.backup_config:
            raise("backup config not given")
        
        #Qos attributes
        self.latency = data['latency']
        self.comp_req = data['comp_req']
    
    def replication_strat(self):
        """implements the stratergy named in self.mechanism"""
        
        raise NotImplementedError()