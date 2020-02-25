"""it is an example ft_unit that implements active replication and is reliable"""

from .base import ReplicationStratergy, FaultDetectionStratergy, FtUnit

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Exchange")

class Replication(ReplicationStratergy):
    """extends the ReplicationStratergy class inherited from base"""

    pass

class FaultDetection(FaultDetectionStratergy):
    """extends the FaultDetectionStratergy base class"""

    pass

class ReliableFtUnit(FtUnit):
    """extends the FtUnit base class"""

    pass