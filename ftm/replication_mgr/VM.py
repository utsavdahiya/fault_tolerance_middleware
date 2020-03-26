'''VM class which defines the property of VM object'''

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VM:
    def __init__(self, id, config):
        self.id = id
        self.config = config
        self.status = 'inactive'