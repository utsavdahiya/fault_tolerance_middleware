'''to invoke the required number of replicas(via the resource manager) and return a list of them
    it receives the requirements from composition engine and returns the list to it
'''
from .VM import VM
from termcolor import colored

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
    async def instantiate_replicas(cls, ft_unit, ftm, vm_placement):
        '''asks resource manager to invoke specified configs

        Returns:
            VMs: a dict containing primary and backup VM ids
        '''
        #ft_unit.replication_strat.num_of_replica contains the default num of replicas to be invoked
        logger.debug(colored("instantiating replicas", 'blue', 'on_white'))

        num_primary = ft_unit.replication_strat.num_of_primary
        num_backup = ft_unit.replication_strat.num_of_replica
        primary_config = ft_unit.replication_strat.primary_config #it is a list of json
        # backup_config = ft_unit.replication_strat.backup_config #it is a json
        #invoke the required VMs and their backups(replicas)
        for vm_parameter in ft_unit.replication_strat.primary_config:
            config = vm_parameter['config']
            loc = vm_placement['primary']['loc']
            config['location'] = loc
            vm = VM(config)
            vm.location = loc
            logger.info(colored(f"created a primary VM id: {vm.id}", 'blue'))
            VMs = {}
            VMs[vm.id] = []
            ftm.all_VMs[vm.id] = vm     #registering VM with ftm
            # ftm.VMs[vm.id] = []
            #instantiating primary
            id, code = await ftm.resource_mgr.instantiate(ftm, vm)
            logger.info(colored(f"instantiated vm[{vm.id}] at location [{vm.location}]", 'blue'))
            for location in vm_placement['primary']['backup'].keys():
                for num_replica in range(vm_placement['primary']['backup'][location]):
                    config['location'] = location
                    backup_vm = VM(config)
                    vm.location = location
                    ftm.all_VMs[backup_vm.id] = backup_vm
                    logger.info(colored(f"created a primary VM with id: {backup_vm.id}", 'blue'))

                    id, code = await ftm.resource_mgr.instantiate(ftm, backup_vm)
                    logger.info(colored(f"instantiated vm[{backup_vm.id}] at location [{vm.location}]", 'blue'))
                    VMs[vm.id].append(backup_vm.id)
            ftm.VMs.append(VMs)

        # for primary_vms in vm_placement['primary']:
        #     config = ft_unit.replication_strat.primary[i]
        #     num_of_vm = config_group[1]
        #     for item in range(num_of_vm):   #instantiating 'num_of_vm' number of VMs of type 'config_group[0]
        #         #create a VM object
        #         if(config_group[0] == 'primary'):
        #             vm = VM(primary_config)
        #         elif(config_group[0] == 'backup'):
        #             vm = VM(backup_config)
        #         else:
        #             raise(f"{config_group[0]}is not a valid config type, should be primary or backup")
        #         #call resource manager to allocate this VM in cloud
        #         id, code = await ftm.resource_mgr.instantiate(ftm, vm)
        #         if(code == 'SUCCESS'):
        #             logger.info(f"VM:{vm.id} was instantiated successfully")
        #         elif(code == 'FAILURE'):
        #             logger.info(f"VM:{vm.id} could not be instantiated some error occured")
        #         else:
        #             raise(f"inavlid error code when trying to instantiate VM:{vm.id}")