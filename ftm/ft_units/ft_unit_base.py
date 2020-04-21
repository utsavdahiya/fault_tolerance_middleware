"""this is the base class for ft_units
ft_unit is the basic module that implements any and all fault tolerant stratergies 
it gives a template for the stratergy that is then realised by replication manager and fault detection manager
"""
from termcolor import colored
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("__name__")
logger.setLevel(logging.DEBUG)

class VmPlacementPolicy():
    def __init__(self, mech_name):
        self.mech_name = mech_name
        pass
    def place(self, locations, num_primary: int, num_backup: int) -> dict:
        '''decides how to place VMs according to geographical locations'''
        pass

class ReplicationStratergy:
    """base class for replication stratergy"""

    def __init__(self, mech_name: str, data: dict):
        """initialises variables
        
            mech_name:str- the name/id of the chosen mechanism
            data:<key:value>- dict(hashmap) of required paramters for the strat. 
                        eg- {num_of_replica:5, primary_config:<config>, backup_config:<config>}
        """
        logger.debug(colored("creating ReplicationStratergy object", 'blue', 'on_white'))
        try:
            logger.debug(colored(f"data recvd: {data}", 'blue', 'on_white'))
        except Exception as e:
            print(f"error: {e}")
        self.mech_name = mech_name   #type:str- placeholder for actual mechanism implementaion object
        self.num_of_primary = data.get('num_of_primary', None)
        self.num_of_replica = data.get('num_of_replica', None)
        self.primary_config = data.get('primary', None)
        self.backup_config = data.get('backup_config', None) 
        self.replica_ratio = 2
        
        #Qos attributes
        self.latency = data.get('latency', None)
        self.availability = data.get('availability', None)
        self.comp_req = data.get('comp_req', None)
    
    def synchronizer(self, ftm, message):
        """implements the stratergy named in self.mechanism"""

        raise NotImplementedError()

class FaultDetectionStratergy:
    """base class for a fault detection stratergy; meant to be inherited"""

    def __init__(self, mech_name, data):
        self.mech_name = mech_name    #type:str just a name for the mechanism
        #a few attributes of the chosen stratergy
        self.latency = data.get('latency', None)    #avg time taken bw occrance and detection of a fault
        self.comp_req = data.get('comp_req', None)  #the computaional requirements of the strat

    async def detection_strat(self):
        """"implements the stratergy named in self.mechanism"""

        raise NotImplementedError()

class FtUnit:
    """Base class for ft_unit"""

    def __init__(self, id, replication_strat, detection_strat, vm_placement_policy):
        self.id = id

        self.replication_strat = replication_strat  #type:ReplicationStratergy instance
        self.fault_detection_strat = detection_strat    #type:FaultDetectionStratergy instance
        self.vm_placement = vm_placement_policy
        self.cost_factor = 1
        # self.latency = self.replication_strat.latency + self.fault_detection_strat.latency  #it is a function of all components
        self.latency = "latency"
        self.qos = {"latency" : self.replication_strat.latency,
                "bandwidth" : 0,
                "availability" : self.replication_strat.availability,
                "comp_req": self.replication_strat.comp_req}
        
    def value(self):
        """returns the quality values of the ft_unit for ranking it"""

        return self.qos
    
    async def instantiate_unit(self, requirements):
        pass

    def populate(self,  requirements):
        '''populate the required fields of the stratergies and ft_unit using the requirements'''
        pass

    def demo(self):
        print("printing from ft_unit")