'''VM class which defines the property of VM object'''

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_id(counter):
    #return a unique id based on counter
    pass

#can implement VM using a state mahchine in future, might be easier to keep track of the states of a VM
class VM:
    counter = 0
    def __init__(self, config):
        VM.counter += 1
        self.id = str(VM.counter)
        self.primary_vm_id = self.id
        self.config = config    #a dictionary of config
        '''config = {
                "mips": "1000",
                "pes": "4",
                "ram": "1000",
                "bandwidth": "1000",
                "size": "10000",
                "location": "1"
            }
'''
        self.status = 'inactive'    #inactive(not running)/active(running)
        self.location = None