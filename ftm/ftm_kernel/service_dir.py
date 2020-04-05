'''
    it maintains a list of ft_units that have been predefined

    <input>
        gets a set of requirements(contrainsts) from the user

    <output>
        it returns a list of eligible ft_units
'''
from ft_units import ft_unit_base

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("__name__")

class ServiceDirectory():

    def __init__(self):
        #possibly change self.ft_units to a set data structure?
        self.ft_units = {}  #a hashmap of <ft_unit_name: ft_unit_object>
        #adding demo unit
        self.ft_units['demo'] = 'demo ft_unit'
    
    def add_unit(self, ft_unit: ft_unit_base.FtUnit):
        """adds an ft_unit to the service directory
            
            Args:
                ft_unit: A class ft_unit object
        """
        id = ft_unit.get_id()
        self.ft_units[id] = ft_unit
        logger.info("added " + id + " to directory")

    def find_eligible_units(self, requirements: dict) -> list:
        '''searches self.ft_units for eligible ft_units
        
            Args:
                requirements: a dict of client's requirements
            '''
        #for each val in req, find all matching ft_units
        pass