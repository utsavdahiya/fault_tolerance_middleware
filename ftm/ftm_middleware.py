'''FTM middleware that will perform the workings of FTM'''
from ftm_kernel import service_dir, composition_engine, evaluation_unit
from replication_mgr import replica_invoker
from resource_mgr import ResouceManager
from ft_units import *

import asyncio

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FTM:
    counter = 0 #used for generating a unique id
    def __init__(self, msg_monitor, client_id):
        FTM.counter += 1
        self.id = str(FTM.counter)
        self.client_id = client_id
        self.resource_mgr = ResouceManager(msg_monitor)
        self.service_directory = service_dir.ServiceDirectory()
        self.composition_engine = composition_engine.CompositionEngine()
        self.ft_unit = None

    async def create_ft_unit(self, requirements: dict) -> list:
        '''procedure to create ft_unit from given user reqs
        
           Args:
            requirements: a dictionary(hashmap) of client requirments'''
        eligible_ft_units = self.service_directory.find_eligible_units()    #returns a list of ft_units
        to_be_deployed = self.composition_engine.compose_solution(eligible_ft_units)
        #send to_be_deployed to resource manager to instantiate

async def start_ftm(client_id, msg_monitor, requirements):
    '''To start initialise the ftm middleware: going from client requirments to invoked VMs
    Args:
        msg_moinitor: is a MesasgingMonitor object associated with the application
        requirements: dict of client requirments
            example: {"vms": [{"num_of_instances": "num",
                            "config": {"mips": "1000",
                                    "pes": "4",
                                    "ram": "1000",
                                    "bandwidth": "1000",
                                    "size": "10000",
                                    "location": "1"}
                        }],
                "latency": "low",
                "availability": "high",
                "bandwidth": "moderate"
            }
    '''
    logger.info("starting ftm application for new client")
    #create a new ftm object
    ftm = FTM(msg_monitor, client_id)
    #the flow of control of FTM:
    eligible_units = await ftm.service_directory.find_eligible_units(requirements)
    if len(eligible_units) == 0:
        raise("No eligible unit found, maybe you would like to create your own")
    chosen_unit = await ftm.composition_engine.compose_solution(eligible_units, requirements)
    ftm.ft_unit = chosen_unit

    #invoke the required VMs using predefined VM placement ploicy, replication and fault detection policies
    #or you can include custom replication and fault detection policy here
    # example: chosen_unit.repllication_strat = my_stratergy | derived from replication_mgr
    replica_invoker.invoker().instantiate_replicas(ftm.ft_unit, requirements, ftm)
    return ftm