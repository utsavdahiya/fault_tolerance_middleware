'''
    it maintains a list of ft_units that have been predefined

    <input>
        gets a set of requirements(contrainsts) from the user

    <output>
        it returns a list of eligible ft_units
'''
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("__name__")

class ServiceDirectory():

    def __init__(self):
        self.ft_units = {}  #a hashmap of <ft_unit_name: ft_unit_object>
    
    def add_unit(self, ft_unit):
        """adds an ft_unit to the service directory
            
            Args:
                ft_unit: An object of ft_unit
        """
        id = ft_unit.get_id()
        self.ft_units[id] = ft_unit
        logger.info("added " + id + " to directory")