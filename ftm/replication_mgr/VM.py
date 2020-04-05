'''VM class which defines the property of VM object'''

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_id(counter):
    #return a unique id based on counter
    pass

#can implement VM using a state mahchine in future, might be easier to keep track of the states of a VM
class VM:
    counter = 1
    def __init__(self, id, config):
        VM.counter += 1
        self.id = VM.counter
        self.config = config
        self.status = 'inactive'    #inactive(not running)/active(running)