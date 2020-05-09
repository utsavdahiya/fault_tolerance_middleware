from ftm.server import run_main as server_main
from ftm.websocket_client import run_main as client_main
from ftm import globals
# from ftm.test_cloud import run_main as cloud_main

from termcolor import colored
import subprocess, shlex
import multiprocessing
import time
import json

command = "python test.py"
def subprocess_cmd(command, cwd=None, **kwargs):
    if 'queue' in kwargs:
        queue = kwargs['queue']
    process = subprocess.Popen(command.split(), cwd=cwd, stdout=subprocess.PIPE, text=True)
    # output = process.stdout
    # error = process.stderr
    output, error = process.communicate()
    print(f"output: {output} \nerror: {error}")

# def subprocess_cmd(command):
#     process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
#     proc_stdout = process.communicate()[0].strip() 
#     print(proc_stdout)

# subprocess_cmd(command)

def procedure(RUN):
    queue = multiprocessing.Queue()
    cmd2 = "python server.py arg1 arg2 arg 3"
    classname = "Client"
    # arguments = "/home/uday-vig/fault_tolerance_middleware/CloudSim_Conf"
    arguments = f"/home/uday-vig/fault_tolerance_middleware/CloudSim_Config.json&{RUN}"
    cmd3 = f'mvn exec:java -f CloudSimInterface/ -Dexec.mainClass={classname} -Dexec.args="{arguments}"'
    # cmd3 = f"mvn exec:java -Dexec.mainClass={classname} -Dexec.args={arguments}"
    cmd4 = "python websocket_client.py"
    # p1 = multiprocessing.Process(target=subprocess_cmd, args=(cmd2, "../"))
    p2 = multiprocessing.Process(target=subprocess_cmd, args=(cmd3,))
    # p3 = multiprocessing.Process(target=subprocess_cmd, args=(cmd4, "../"))
    p1 = multiprocessing.Process(target=server_main, args=(queue,))
    # p2 = multiprocessing.Process(target=cloud_main)
    p3 = multiprocessing.Process(target=client_main, args=(queue,))
    
    p1.start()  #starting server
    time.sleep(4)
    p2.start()  #starting cloud
    resp = queue.get()
    print(colored(f"Server process says: {resp}", 'yellow'))
    time.sleep(2)

    p3.start()  #starting client
    p1.join()
    print("xxxxxxxxxxxxxx FTM finished xxxxxxxxxxxxxxxxx")
    queue.put("quit")
    print("p1 finished")
    p3.join()
    print("xxxxxxxxxxxxxx Client finished xxxxxxxxxxxxx")
    p2.join()
    print("xxxxxxxxxxxxxx CloudSim finished xxxxxxxxxxxxxx")

def run_main():
    NUM_SIMULATION = 10
    EPOCH = 10
    NUM_LOCATIONS = 4
    OUTPUT = "./results/OutputUday21.pkl"
    SIMULATION_TIME = 38
    ARCH = "original"    #can change to "original"
    PORT_CLOUD = '9081'
    PORT_CLIENT = '9082'
    # CONFIG_FILE = "config1.conf"

    RUN = '1'
    THRESHOLD1 = 0.5    #used for host threshold over the dist by SEED1
    THRESHOLD2 = 0.7
    SEED1 = 42  #used for host fault injection porb uniform distribution
    SEED2 = 42
    SEED3 = 42
    SEED4 = 42
    LOCATIONS_DOWN = 0
    NUM_HOSTS = 50

    FAULT_RATE = 0.8
    THRESHOLD1 = 1.0 - float(FAULT_RATE)/NUM_HOSTS
    # fault_rate = (1 - THRESHOLD1) * (1 - THRESHOLD2) * float(NUM_LOCATIONS)

    first_run = True
    first_cloud_run = True

    for iteration in range(NUM_SIMULATION):
        SEED2 = 42
        for epoch in range(EPOCH):
            print(f"Iteration: {iteration} | epoch: {epoch}")
            # with open("ftm.conf") as handle:
            #     settings = json.load(handle)
            
            THRESHOLD1 = 1.0 - float(FAULT_RATE)/NUM_HOSTS
            # fault_rate = (1 - THRESHOLD1) * (1 - THRESHOLD2) * float(NUM_LOCATIONS)

            settings = {}
            settings['FAULT_RATE'] = FAULT_RATE
            settings['EPOCH'] = epoch
            settings['SIMULATION_TIME'] = SIMULATION_TIME
            settings['ARCH'] = ARCH
            settings['OUTPUT'] = OUTPUT
            settings['NUM_LOCATIONS'] = NUM_LOCATIONS
            if first_run:
                first_run = False
                settings['PORT_CLOUD'] = PORT_CLOUD
                settings['PORT_CLIENT'] = PORT_CLIENT

            # with open(CONFIG_FILE, '+w') as handle:
            #     print(f"updating {CONFIG_FILE}: {settings}")
            #     json.dump(settings, handle)
            # globals.initialize_globals("ftm.conf")
            globals.initialize_globals(settings)

            cloud_args = {
                            "threshold1" : str(THRESHOLD1),
                            "threshold2" : str(THRESHOLD2),
                            "seed1" : str(SEED1),
                            "seed2" : str(SEED2),
                            "seed3" : str(SEED3),
                            "seed4" : str(SEED4),
                            "port" : PORT_CLOUD,
                            "num_locations" : str(NUM_LOCATIONS),
                            "num_locations_down" : str(LOCATIONS_DOWN),
                            "num_hosts" : str(NUM_HOSTS)
                        }
            # if first_cloud_run:
            # 	first_cloud_run = False
            # 	cloud_args['port'] = PORT_CLOUD

            with open("CloudSim_Config.json") as handle:
                print(f"updating CloudSim_Conf: {json.dumps(cloud_args, indent=2)}")
                # json.dump(cloud_args, handle, indent=2)
                params = json.load(handle)
            if RUN == '0':
                params['array'][0] = cloud_args
            else:
                params['array'][1] = cloud_args

            with open("CloudSim_Config.json", 'w') as outfile:
                json.dump(params, outfile, indent=2)

            procedure(RUN)

            print(colored(f"\n\n\n\n-----------------------------EPOCH COMPLETED---------------------------\n\n\n", 'green'))
            time.sleep(4)
            SEED1 += 1
            SEED2 += 1
            SEED3 += 1

        #updating the parameters
        # THRESHOLD2 -= 0.03
        FAULT_RATE += 0.2

if __name__ == '__main__':
    run_main()
