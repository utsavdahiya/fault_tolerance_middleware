'''
    it maintains a list of ft_units that have been predefined

    <input>
        gets a set of requirements(contrainsts) from the user

    <output>
        it returns a list of eligible ft_units
'''
from ft_units.ft_unit_base import FtUnit
from ft_units import reliable
from termcolor import colored

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("__name__")
logger.setLevel(logging.DEBUG)

class ServiceDirectory():

    def __init__(self):
        logger.debug(colored("creating a ServiceDiectory object", 'blue', 'on_white'))

        #possibly change self.ft_units to a set data structure?
        self.ft_units = {}  #a hashmap of <ft_unit_name: ft_unit_object>
        #adding demo unit
        # self.ft_units['demo_unit'] = 'demo ft_unit'
        logging.debug(colored("calling reliable to create a ft_unit", 'blue', 'on_white'))
        self.ft_units['reliable_ft_unit'] = reliable.create_ft_unit()
    
    def add_unit(self, ft_unit):
        """adds an ft_unit to the service directory
            
            Args:
                ft_unit: A class ft_unit object
        """
        id = ft_unit.id
        self.ft_units[id] = ft_unit
        logger.info("added " + id + " to directory")

    async def find_eligible_units(self, requirements: dict) -> list:
        '''searches self.ft_units for eligible ft_units
        
            Args:
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
        logger.info(colored(f"service directory is searching for eligible ft_units matching your requirements", 'blue'))
        
        #for each val in req, find all matching ft_units
        logger.debug(colored(f"following ft_units are available: {self.ft_units.keys()}", 'blue', 'on_white'))
        eligible_units = []
        for unit_name, unit in self.ft_units.items():
            if ((unit.qos['latency'] == requirements['latency']) and (unit.qos['availability'] == requirements['availability'])):
                logger.debug(colored("one unit found", 'blue', 'on_white'))
                unit.populate(requirements)
                eligible_units.append(unit)
        
        return eligible_units