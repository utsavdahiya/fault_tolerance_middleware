import json

NUM_LOCATIONS = 10
CONFIG_NUMBER = 1
FAULT_CONFIG = 1
ITERATION = 1
EPOCH = 1
SIMULATION_TIME = 40
OUTPUT = "./default_output"

def initialize_globals(args):
    print(f"Arguements passed: {args}")

    fname = f"../run/{args[1]}"
    with open(fname) as handle:
        args = json.load(handle)

    if 'NUM_LOCATIONS' in args:
        global NUM_LOCATIONS
        NUM_LOCATIONS = args['NUM_LOCATIONS']
    if 'FAULT_CONFIG' in args:
        global FAULT_CONFIG
        FAULT_CONFIG = args['FAULT_CONFIG']
    if 'CONFIG_NUMBER' in args:
        global CONFIG_NUMBER
        CONFIG_NUMBER = args['CONFIG_NUMBER']
    if 'ITERATION' in args:
        global ITERATION
        ITERATION = args['ITERATION']
    if 'EPOCH' in args:
        global EPOCH
        EPOCH = args['EPOCH']
    if 'OPUTPUT' in args:
        global OUTPUT
        OUTPUT = args['OUTPUT']
    if 'SIMULATION_TIME' in args:
        global SIMULATION_TIME
        SIMULATION_TIME = args['SIMULATION_TIME']