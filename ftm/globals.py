import json

NUM_LOCATIONS = 10
CONFIG_NUMBER = 1
FAULT_RATE = 5
ITERATION = 1
EPOCH = 1
SIMULATION_TIME = 40
ARCH = "new"
PORT_CLOUD = '80801'
PORT_CLIENT = '8082'
LOCATIONS = {}
OUTPUT = "./results/default_output.pkl"

def initialize_globals(args):
    print("---INITTIALIZING GLOBAL VARS---")
    print(f"Arguements passed: {args}")

    # fname = f"{args}"
    # with open(fname) as handle:
    #     args = json.load(handle)

    if 'NUM_LOCATIONS' in args:
        global NUM_LOCATIONS
        NUM_LOCATIONS = args['NUM_LOCATIONS']
    if 'FAULT_RATE' in args:
        global FAULT_RATE
        FAULT_RATE = args['FAULT_RATE']
    if 'CONFIG_NUMBER' in args:
        global CONFIG_NUMBER
        CONFIG_NUMBER = args['CONFIG_NUMBER']
    if 'ITERATION' in args:
        global ITERATION
        ITERATION = args['ITERATION']
    if 'EPOCH' in args:
        global EPOCH
        EPOCH = args['EPOCH']
    if 'OUTPUT' in args:
        global OUTPUT
        OUTPUT = args['OUTPUT']
    if 'SIMULATION_TIME' in args:
        global SIMULATION_TIME
        SIMULATION_TIME = args['SIMULATION_TIME']
    if 'ARCH' in args:
        global ARCH
        ARCH = args['ARCH']
    if 'LOCATIONS' in args:
        global LOCATIONS
        LOCATIONS = args['LOCATIONS']
    if 'PORT_CLOUD' in args:
        global PORT_CLOUD
        PORT_CLOUD = args['PORT_CLOUD']
    if 'PORT_CLIENT' in args:
        global PORT_CLIENT
        PORT_CLIENT = args['PORT_CLIENT']