'''
    it formulates a solution as well as instantiates the reqd policy adhereing to client requirements from given ft_units

    <input>
        >a list of ft_units
        >user requirements
    <output>
        >return
'''
from ..ft_units.ft_unit_base import FtUnit
from termcolor import colored

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class CompositionEngine():
    '''creates a ft_unit solution from eligible ft_units'''
    def __init__(self):
        logger.debug(colored("creating a CompositionEngine object", 'blue', 'on_white'))
        pass

    async def compose_solution(self, ft_units: list, requirements) -> FtUnit:
        '''compose a suitable solution from given eligible ft_units
        
            Args:
                ft_units: a list of eligible ft_units(staisfying user requirements)
                requirements: the requirements as given by the user
            Return:
                returns an ft_unit that is chosen to be enforced
        '''
        logger.info(colored("composing a solution using eligible units", 'blue'))
        #do trivial sort of the ft_units
        chosen_unit = ft_units[0]
        #return the topmost
        return chosen_unit