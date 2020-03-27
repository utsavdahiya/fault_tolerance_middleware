'''to invoke the required number of replicas(via the resource manager) and return a list of them
    it receives the requirements from composition engine and returns the list to it
'''
from .VM import VM

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    def instantiate_replicas(self, config_info, app):
        '''asks resource manager to invoke specified configs
        
        once the VMs have been invoked it also registers them with the app
        Args:
            config_info: A list of tuples of config names(IDs) to be invoked(instantiated):
                example: [(config_type, number of VMs to be invoked), (), ...]
                    config_type is an identifier(str) such as primary config etc
            app: the instance of app object from within which this function has been called
        Returns:
            VMs: a dict of list of VMs according the config names as received in confid_info:
                example: {config_type: [VMs of type config_type that have been invoked]}
        '''
        VMs = dict()
        for item in config_info:
            vm_list = []
            for i in range(item[1]):
                config_name = item[0]
                config = self.configs.get(config_name)
                #create a new VM object
                vm = VM(id, config)
                #call resource manager to get resources allocated from the 
                app.self.VMs[id] = vm
                vm_list.append(vm)
            VMs[item[0]] = vm_list
        return VMs