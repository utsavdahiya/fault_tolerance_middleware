'''to invoke the required number of replicas(via the resource manager) and return a list of them
    it receives the requirements from composition engine and returns the list to it
'''

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class invoker:
    '''class to invole the replicas'''
    def __init__(self):
        self.configs = []   #list of <conifg_name: config_json>
        self.default_config = {}    #a json of config

    def add_config(self, configs):
        pass
