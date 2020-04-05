'''VM class which defines the property of VM object'''

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_id(counter):
    #return a unique id based on counter
    pass

class VM:
    counter = 1
    def __init__(self, id, config):
        counter += 1
        self.id = get_id(counter) 
        self.config = config
        self.status = 'inactive'    #inactive(not running)/active(running)