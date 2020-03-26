'''to invoke the required number of replicas(via the resource manager) and return a list of them
    it receives the requirements from composition engine and returns the list to it
'''
from .VM import VM

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_id():
    pass

class invoker:
    '''class to invole the replicas'''
    def __init__(self):
        self.configs = []   #list of <conifg_name: config_json>
        self.default_config = {}    #a json of config

    def add_config(self, configs):
        '''adds a new configuration to the invoker
        
        Args:
            configs: A list of dictionaries containing replication config:
                    example: [{config_name: {config_json}}, {}, ...]
        '''
        for item in configs:
            if item not in self.configs:
                for name, config in item:
                    self.configs[name] = config     #add config to self.configs

    def instantiate_replicas(self, config_info):
        '''asks resource manager to invoke specified configs
        
        Args:
            config_info: A list of tuples of config names(IDs) to be invoked(instantiated):
                example: [(config_name, number of VMs to be invoked), (), ...]
        '''
        VMs = dict()
        for item in config_info:
            vm_list = []
            for i in range(item[2]):
                id = get_id()
                config_name = item[0]
                config = self.configs.get(config_name)
                #create a new VM object
                vm = VM(id, config)
                
