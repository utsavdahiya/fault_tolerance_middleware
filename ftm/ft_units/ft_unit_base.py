"""this is the base class for ft_units

ft_unit is the basic module that implements any and all fault tolerant stratergies 
it gives a template for the stratergy that is then realised by replication manager and fault detection manager
"""
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("__name__")

class VmPlacementPolicy():
    def __init__(self):
        pass
    def place(self, num_primary: int, num_backup: int) -> list:
        '''decides how to place VMs according to geographical locations'''
        pass

class ReplicationStratergy:
    """base class for replication stratergy"""

    def __init__(self, mech_name, data):
        """initialises variables
        
            mech_name:str- the name/id of the chosen mechanism
            data:<key:value>- dict(hashmap) of required paramters for the strat. 
                        eg- {num_of_replica:5, primary_config:<config>, backup_config:<config>}
        """
        self.mech_name = mech_name   #type:str- placeholder for actual mechanism implementaion object
        self.num_of_replica = data['num_of_replica']
        self.backup_config = data['backup_config'] #a list of configurations(YAML file) for backup VMs
        self.replica_ratio = 2
        
        #Qos attributes
        self.latency = data['latency']
        self.comp_req = data['comp_req']
    
    def replication_strat(self):
        """implements the stratergy named in self.mechanism"""

        raise NotImplementedError()

class FaultDetectionStratergy:
    """base class for a fault detection stratergy; meant to be inherited"""

    def __init__(self, mech_name, data):
        self.mech_name = mech_name    #type:str just a name for the mechanism
        #a few attributes of the chosen stratergy
        self.latency = data['latency']    #avg time taken bw occrance and detection of a fault
        self.comp_req = data['comp_req']  #the computaional requirements of the strat

    def detection_strat(self):
        """"implements the stratergy named in self.mechanism"""

        raise NotImplementedError()

class FtUnit:
    """Base class for ft_unit"""

    def __init__(self, id, replication_strat, detection_strat):
        self.id = id

        self.replication_strat = replication_strat  #type:ReplicationStratergy instance
        self.fault_detection_strat = detection_strat    #type:FaultDetectionStratergy instance
        self.cost_factor = 1
        # self.latency = self.replication_strat.latency + self.fault_detection_strat.latency  #it is a function of all components
        self.latency = "latency"
        self.qos = {"latency" : self.latency,
                "bandwidth" : 0,
                "availability" : 0}
        
    def value(self):
        """returns the quality values of the ft_unit for ranking it"""

        return self.qos
    
    async def instantiate_unit(self, requirements):
        pass

    def populate(self, requirements):
        '''populate the required fields of the stratergies and ft_unit using the requirements'''
        pass

    def demo(self):
        print("printing from ft_unit")