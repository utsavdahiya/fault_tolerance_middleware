'''FTM middleware that will perform the workings of FTM'''
from ftm import globals
from .ftm_kernel import service_dir, composition_engine, evaluation_unit
from .replication_mgr import replica_invoker
from .resource_mgr import ResouceManager
from .ft_units import *
from .fault_masking_mgr import FaultMasking

# from ftm.server import CONFIG_NUMBER, FAULT_CONFIG, NUM_LOCATIONS, CONFIG_NUMBER, FAULT_CONFIG, ITERATION, EPOCH, OUTPUT

import sys
import pickle
import numpy as np
from bitarray import bitarray
from timeit import default_timer
from prettytable import PrettyTable
from termcolor import colored
import asyncio
import json
from timeit import default_timer

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
        self._queue = asyncio.Queue()
        self.client_id = client_id
        self.msg_monitor = msg_monitor
        # self.monitor_list = []
        self.resource_mgr = ResouceManager(msg_monitor)
        self.service_directory = service_dir.ServiceDirectory()
        self.composition_engine = composition_engine.CompositionEngine()
        self.fault_mask_mgr = FaultMasking("migration")
        self.ft_unit = None
        self.all_VMs = {}   #a dict of all VMs <vm_id: vm_obj>
        self.VMs = []   #a list of VMs asked by client [{primary_vm_id: [list of replica VMs]}]
        self.availability = {}  #dict to calc availability <primary_vm_id: bitarray>
        self.simulation_start_time = default_timer() + 9
        # self.SIMULATION_TIME = 40

        asyncio.create_task(self.setup())

    async def setup(self):
        #start queue
        while True:
            item = await self._queue.get()
            if item is None:
                continue
            action = item.get('action').upper()
            data = item.get('data', {})
            callaback = item.get('callback', None)
            # logger.info(colored(f"New action: {action}",'blue', 'on_white'))

            if action == 'STATUS':
                asyncio.create_task(self.evaluate_status(data))
            elif action == 'FAULT MASK':
                asyncio.create_task(self.fault_mask_mgr.handle_fault(data))
            elif action == "HOST ALLOCATION":
                asyncio.create_task(self.activate_vm(data))
            elif action == 'MIGRATION SUCCESSFUL':
                asyncio.create_task(self.migration_successful(data))
            else:
                raise Exception(colored(f"no fucntion defined for action: {action}", 'red'))

    async def migration_successful(self, data):
        vm_id = data['mv_id']
        #set condition to working
        self.all_VMs[vm_id].status = "working"

    async def activate_vm(self, data):
        logger.debug(colored(f"activating vm[{data['vm_id']}]", "blue", "on_white"))
        vm_id = data['vm_id']
        self.all_VMs[vm_id].status = "active"   #acitvate the vm
        primary_vm_id = self.all_VMs[vm_id].primary_vm_id
        if primary_vm_id not in self.availability:
            #initailise the bitarray
            self.availability[primary_vm_id] = (self.ft_unit.replication_strat.replica_ratio + 1) * bitarray('0')
        bitset = self.availability[primary_vm_id]
        offset = int(primary_vm_id) % len(bitset)
        pos = (int(vm_id) % len(bitset)) - offset
        #setting the bit corressponding to vm_id
        bitset[pos] = True
        #add vm to monitoring list
        if vm_id not in self.resource_mgr.monitor_list:
            self.resource_mgr.monitor_list.append(vm_id)
        logger.info(colored(f"vm[{vm_id}] has been activated"))

    async def evaluate_status(self, data, callaback=None):
        '''
            {   
                "client_id": "id of client"
                "desc": "status",
                "allocated_bandwidth":"10000", 
                "available_bandwidth":"10000",
                "capacity_bandwidth":"20000",
                "current_requested_bandwidth":"20000",
                "cpu_percent_utilization":"80",
                "current_requested_total_mips":"500",
                "allocated_ram":"4096",
                "available_ram":"8192",
                "capacity_ram":"8192",
                "current_requested_ram":"8192",
                "allocated_storage":"12800",
                "available_storage":"25600",
                "capacity_storage":"25600",
                "condition":"working"
            }
        '''
        vm_status = data
        vm_status['ftm'] = self
        if vm_status['condition'] != "working":
            logger.info(colored(f"vm[{data['vm_id']}] condition is not working!!", 'red'))
            if self.all_VMs[data['vm_id']].status == 'active':
                #if the VM was active until now, then try to mask fault
                await self._queue.put({'action': 'FAULT MASK', 'data': vm_status})
            else:
                #this is duplicate status message, fault handling for this VM has already been initiated above
                #incrementing the failure count of the VM
                self.all_VMs[data['vm_id']].fail_counter += 1
                if self.all_VMs[data['vm_id']].fail_counter > self.fault_mask_mgr.MIGRATION_FAILURE_THRESHOLD:
                    #reset the counter again after sending migration req
                    self.all_VMs[data['vm_id']].fail_counter = 0
                    await self._queue.put({'action': 'FAULT MASK', 'data': vm_status})
        # elif vm_status['cpu_percent_utilization'] > 95:
        #     await self._queue.put({'action': 'FAULT MASK', 'data': vm_status})
        # elif vm_status['allocated_ram']/vm_status['capacity_ram'] > 90:
        #     await self._queue.put({'action': 'FAULT MASK', 'data': vm_status})
        else:
            logger.info(colored(f"vm[{data['vm_id']}]STATUS OK", 'green', 'on_white'))
            #rest the failure counter once the VM is working
            self.all_VMs[data['vm_id']].fail_counter = 0
            if self.all_VMs[data['vm_id']].status != "active":
                vm_id = data['vm_id']
                self.all_VMs[vm_id].status = "active"   #acitvate the vm
                primary_vm_id = self.all_VMs[vm_id].primary_vm_id
                if primary_vm_id not in self.availability:
                    #initailise the bitarray
                    self.availability[primary_vm_id] = (self.ft_unit.replication_strat.replica_ratio + 1) * bitarray('0')
                bitset = self.availability[primary_vm_id]
                offset = int(primary_vm_id) % len(bitset)
                pos = (int(vm_id) % len(bitset)) - offset
                #setting the bit corressponding to vm_id
                bitset[pos] = True
        # else:
        #     logger.info(colored(f"no masking procedure specified", 'red'))

    async def finish(self):
        #stopping the resource manager monitor
        self.resource_mgr.monitor_flag = False
        #printing failure durations
        failures = self.resource_mgr.failures
        total_duration = 0
        table = PrettyTable()
        table.field_names = ["VM ID", "Failure Duration"]
        failure_times = []  #times of occurance of all failures
        failure_durations = []

        for primary_vm, stat in failures.items():
            #primary_vm= primary_vm_d, stat= list of failures
            if stat[0]["flag"] == True:
                #if recovery was pending
                stat[-1].end = default_timer()
            for failure in stat[1:]:
                duration = failure.end - failure.start
                failure_durations.append(duration)
                failure_times.append(failure.start - self.simulation_start_time)
                table.add_row([primary_vm, duration])
                total_duration += duration

        logger.info(f"\n{table}")
        logger.info(colored(f"Total Failure Duration:\t {total_duration}", "green"))

        #post processing of data for storage
        output = globals.OUTPUT
        #processing failure_durations
        num_primary = self.ft_unit.replication_strat.num_of_primary
        mean_failure_duration = np.sum(failure_durations)/num_primary
        availability = 1.0 - (float(mean_failure_duration) / float(globals.SIMULATION_TIME))
        print(colored(f"Availability: {availability}"))
        try:
            with open(output, 'rb') as handle:
                result = pickle.load(handle)
                logger.info(colored(f"FILE OPENED", on_color='on_green'))
        except Exception as e:
            logger.info(colored(f"FILE OPENNING: {e}", 'red'))
            #file not present
            with open(output, 'w+b') as handle:
                result = {}
                logger.info(colored(f"initailising file with dict", 'green'))
                pickle.dump(result, handle)

        if globals.FAULT_RATE not in result:
            result[globals.FAULT_RATE] = {}
            result[globals.FAULT_RATE]['duration'] = []
            result[globals.FAULT_RATE]['timing'] = {}

        result[globals.FAULT_RATE]['duration'].append(availability)
        # with open(output, 'wb') as handle:
        #     pickle.dump(result, handle)

        # #processing the failure times
        # with open('/resutls/failure_times.pkl', 'rb') as handle:
            # failure_result = pickle.load(handle)
        
        # store = failure_result[FAULT_CONFIG]
        for time in range(globals.SIMULATION_TIME):
            if time not in result[globals.FAULT_RATE]['timing']:
                result[globals.FAULT_RATE]['timing'][time] = []
            arr = np.array(failure_times)
            result[globals.FAULT_RATE]['timing'][time].append((arr < time).sum())
        
        # failure_result[FAULT_CONFIG] = store
        with open(output, 'wb') as handle:
            pickle.dump(result, handle)

        logger.info(colored("\n\n\n\n---------------EXITING SERVER---------------------\n\n\n\n", 'magenta'))
        sys.exit()

async def start_ftm(application, client_id, msg_monitor, data):
    '''To start initialise the ftm middleware: going from client requirments to

        data: dict of client requirments and other info
            example: {'client_req': {"vms": [
                                    {"num_of_instances": "num",
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
                    'locations': [list of locations]
            }
    '''
    requirements = data['client_req']
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
    
    #invoke the required VMs using predefined VM placement policy, replication and fault detection policies
    #or you can include custom replication and fault detection policy here
    # example: chosen_unit.repllication_strat = my_stratergy | derived from replication_mgr
    locations = data['locations']
    logger.info(colored(f"chosing locations using vm placement policy", 'blue'))
    if globals.ARCH == "new":
        vm_placement = await ftm.ft_unit.vm_placement.place(locations,
                        ftm.ft_unit.replication_strat.num_of_primary,
                        ftm.ft_unit.replication_strat.replica_ratio)
    elif globals.ARCH == "original":
        vm_placement = await ftm.ft_unit.vm_placement.place_random(locations,
                        ftm.ft_unit.replication_strat.num_of_primary,
                        ftm.ft_unit.replication_strat.replica_ratio)

    logger.info(colored(f"Now invoking the VMs at the chosen locations...", 'blue'))
    await replica_invoker.invoker().instantiate_replicas(ftm.ft_unit, ftm, vm_placement)

    return ftm