'''
    it maintains a list of ft_units that have been predefined

    <input>
        gets a set of requirements(contrainsts) from the user

    <output>
        it returns a list of eligible ft_units
'''
from ft_units.ft_unit_base import FtUnit
from ft_units import reliable

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("__name__")

class ServiceDirectory():

    def __init__(self):
        #possibly change self.ft_units to a set data structure?
        self.ft_units = {}  #a hashmap of <ft_unit_name: ft_unit_object>
        #adding demo unit
        # self.ft_units['demo_unit'] = 'demo ft_unit'
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
        #for each val in req, find all matching ft_units
        for unit in self.ft_units.keys():
            eligible_units = []
            if ((unit.qos['latency'] == requirements['latency']) and (unit.qos['availability'] == requirements['availability'])):
                unit.populate(requirements)
                eligible_units.append(unit)
        
        return eligible_units