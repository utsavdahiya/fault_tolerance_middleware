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

    async def create_ft_unit(self, requirements: dict) -> list:
        '''procedure to create ft_unit from given user reqs
        
           Args:
            requirements: a dictionary(hashmap) of client requirments'''
        eligible_ft_units = self.service_directory.find_eligible_units()    #returns a list of ft_units
        to_be_deployed = self.composition_engine.compose_solution(eligible_ft_units)
        #send to_be_deployed to resource manager to instantiate
