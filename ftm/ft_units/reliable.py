"""it is an ft_unit that implements active replication and is reliable"""

from base import FtUnit

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Exchange")

class ReliableFtUnit(FtUnit):
    pass