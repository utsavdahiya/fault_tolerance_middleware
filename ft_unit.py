#this is the base class for ft_units
# ft_unit is the basic module that implements any and all fault tolerant stratergies 
#it gives a template for the stratergy that is then realised by replication manager and fault detection manager
  
class ft_unit:
    """Base class for ft_unit"""
    def __init__(self):
        self.id = 0
        self.qos = {"latency" : 0,
                "bandwidth" : 0,
                "availability" : 0}
        self.cost_factor = 1
        self.replication_strat = "stratergy_object_placeholder"
        self.fault_detection_strat = "stratergy_object_placeholder"
    
    def value(self):
        """returns the quality values of the ft_unit for ranking it"""
        return self.qos