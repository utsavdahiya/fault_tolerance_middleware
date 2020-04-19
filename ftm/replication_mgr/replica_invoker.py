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

    @classmethod
    async def instantiate_replicas(cls, ft_unit, requirements, ftm):
        '''asks resource manager to invoke specified configs
        
        Args:
            config_info: A list of tuples of config names(IDs) to be invoked(instantiated):
                example: [(config_type, number of VMs to be invoked), (), ...]
                    config_type is an identifier(str) such as primary config etc
        '''
        #ft_unit.replication_strat.num_of_replica contains the default num of replicas to be invoked
        num_primary = requirements['num_primary']
        num_backup = ft_unit.replication_strat.replica_ratio * num_primary
        primary_config = requirements['primary_config'] #it is a json
        backup_config = ft_unit.replication_strat.backup_config #it is a json

        vm_placement = ft_unit.vm_placement_policy.place(num_primary, num_backup)
        '''vm_placement = [('primary', num of primary to be allocated in one rack(int)),
                            ('primary', num of primary),
                            ('backup', num of backups) ...]
        ''' 
        
        #invoke the required VMs and their backups(replicas)
        for config_group in vm_placement:
            num_of_vm = config_group[1]
            for item in range(num_of_vm):   #instantiating 'num_of_vm' number of VMs of type 'config_group[0]
                #create a VM object
                if(config_group[0] == 'primary'):
                    vm = VM(primary_config)
                elif(config_group[0] == 'backup'):
                    vm = VM(backup_config)
                else:
                    raise(f"{config_group[0]}is not a valid config type, should be primary or backup")
                #call resource manager to allocate this VM in cloud
                id, code = await ftm.resource_mgr.instantiate(ftm, vm)
                if(code == 'SUCCESS'):
                    logger.info(f"VM:{vm.id} was instantiated successfully")
                elif(code == 'FAILURE'):
                    logger.info(f"VM:{vm.id} could not be instantiated some error occured")
                else:
                    raise(f"inavlid error code when trying to instantiate VM:{vm.id}")