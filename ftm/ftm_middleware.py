'''FTM middleware that will perform the workings of FTM'''
from ftm_kernel import service_dir, composition_engine, evaluation_unit
from replication_mgr import *
from ft_units import *

import asyncio

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FTM():
    counter = 0
    def __init__(self):
        FTM.counter += 1
        self.id = FTM.counter
        self.service_directory = service_dir.ServiceDirectory()