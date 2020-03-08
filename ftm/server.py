import ftm_kernel.service_dir
import ft_units
import messaging_monitor

import logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class Application():
    def __init__(self, msg_monitor):
        self.msg_monitor = msg_monitor

    def on_connect_client(self):
        """callback on establishing contact with client"""
        pass

    def on_connect_cloud(self):
        pass

    def on_client_msg(self):
        pass

    def on_cloud_msg(self):
        pass

def main():
    unit = ft_units.base.FtUnit("007", "replication", "fault_tolerance")
    unit.demo()

if __name__=='__main__':
   main()