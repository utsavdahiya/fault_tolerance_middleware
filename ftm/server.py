import ftm_kernel.service_dir
import ft_units

import logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("Exchange")

class Application():
    def __init__(self):
        pass

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
    unit = ft_unit.FtUnit("007")
    unit.demo()

if __name__=='__main__':
   main()