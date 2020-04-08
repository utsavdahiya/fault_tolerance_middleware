'''FTM middleware that will perform the workings of FTM'''
from ftm_kernel import service_dir, composition_engine, evaluation_unit
from replication_mgr import replica_invoker
from resource_manager import resource_mgr
from ft_units import *

import asyncio

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FTM:
    counter = 0 #used for generating a unique id
    def __init__(self, msg_monitor: MessagingMonitor):
        FTM.counter += 1
        self.id = FTM.counter
        self.resource_mgr = resource_mgr.ResouceManager(msg_monitor)
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

async def start_ftm(self, msg_monitor: MessagingMonitor, requirements):
    '''To start initialise the ftm middleware: going from client requirments to invoked VMs'''

    #create a new ftm object
    ftm = FTM(msg_monitor)
    #the flow of control of FTM:
    eligible_units = await ftm.service_directory.find_eligible_units(requirements)
    chosen_unit = await ftm.composition_engine.compose_solution(eligible_units)
    ftm.ft_unit = chosen_unit

    #invoke the required VMs using predefined replication and fault detection policies
    #or you can include custom replication and fault detection policy here
    # example: chosen_unit.repllication_strat = my_stratergy | derived from replication_mgr