#this is the base class for ft_units
# ft_unit is the basic module that implements any and all fault tolerant stratergies 
#it gives a template for the stratergy that is then realised by replication manager and fault detection manager

class ft_unit:
    """Base class for ft_unit"""
    id = 0
    qos = {"latency" = 0,
            "bandwidth" = 0,
            "availability" = 0}
    replication_strat = {"mechinsm" = "default_mech",
                         "no_of_replica" = 0}
    fault_detection_strat = {"mechanism" = "default_mech",
                            "timeout" = 0}
    