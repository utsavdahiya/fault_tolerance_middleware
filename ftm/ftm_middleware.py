'''FTM middleware that will perform the workings of FTM'''
from ftm_kernel import service_dir, composition_engine, evaluation_unit
from replication_mgr import replica_invoker
from resource_mgr import ResouceManager
from ft_units import *
from termcolor import colored
import asyncio
import json

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FTM:
    counter = 0 #used for generating a unique id
    def __init__(self, msg_monitor, client_id):
        logger.debug(colored("creating a FTM object", 'blue', 'on_white'))
        FTM.counter += 1
        self.id = str(FTM.counter)
        self.client_id = client_id
        self.msg_monitor = msg_monitor
        self.resource_mgr = ResouceManager(msg_monitor)
        self.service_directory = service_dir.ServiceDirectory()
        self.composition_engine = composition_engine.CompositionEngine()
        self.ft_unit = None
        self.VMs = []

    async def create_ft_unit(self, requirements: dict) -> list:
        '''procedure to create ft_unit from given user reqs
        
           Args:
            requirements: a dictionary(hashmap) of client requirments'''
        eligible_ft_units = self.service_directory.find_eligible_units()    #returns a list of ft_units
        to_be_deployed = self.composition_engine.compose_solution(eligible_ft_units)
        #send to_be_deployed to resource manager to instantiate

async def start_ftm(application, client_id, msg_monitor, requirements):
    '''To start initialise the ftm middleware: going from client requirments to

    git rm -rf --cached .

    git add .
ion
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
    logger.info(colored("starting ftm application for new client", 'blue'))
    #create a new ftm object
    ftm = FTM(msg_monitor, client_id)
    #the flow of control of FTM:
    eligible_units = await ftm.service_directory.find_eligible_units(requirements)
    if len(eligible_units) == 0:
        raise(colored("No eligible unit found, maybe you would like to create your own", 'red'))
    logger.info(colored("passing the eligible units to composition engine", 'blue'))

    chosen_unit = await ftm.composition_engine.compose_solution(eligible_units, requirements)
    ftm.ft_unit = chosen_unit
    logger.info(colored(f"ft_unit:{chosen_unit.id} has been chosen as appropriate fault tolerance policy", 'blue'))
    unit_config = {"ft_unit_id": chosen_unit.id,
                    "replication_stratergy": chosen_unit.replication_strat.mech_name,
                    "fault_detection_stratergy": chosen_unit.fault_detection_strat.mech_name,
                    "vm_placement_policy": chosen_unit.vm_placement.mech_name}
    pretty_print = json.dumps(unit_config, indent=2)
    logger.info(colored(f"ft_unit_config: {pretty_print}", 'blue', 'on_white'))
    
    return ftm
    #get locations from the cloud
    msg = {"desc": "get_location"}
    locations = await application.get_locations()
    # locations = await ftm.msg_monitor.send_json(msg, 'cloud')
    

async def cont_ftm(ftm, locations):
    # locations = [int(i) for i in locations]     #converting from str to int

    #invoke the required VMs using predefined VM placement policy, replication and fault detection policies
    #or you can include custom replication and fault detection policy here
    # example: chosen_unit.repllication_strat = my_stratergy | derived from replication_mgr
    logger.debug(colored(f"called cont_ftm with the locations: {locations}", 'blue', 'on_white'))
    vm_placement = ftm.ft_unit.vm_placement.place(locations,
                    ftm.ft_unit.replication_strat.num_of_primary,
                    ftm.ft_unit.replication_strat.num_of_replica)

    VMs = replica_invoker.invoker().instantiate_replicas(ftm.ft_unit, ftm, vm_placement)
    ftm.VMs.append(VMs) #register the VMs with ftm

    #starting the resource manager monitoring for the ftm
    await ftm.resource_mgr.monitor()

    return ftm