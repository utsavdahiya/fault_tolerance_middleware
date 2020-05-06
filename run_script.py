from ftm.server import run_main as server_main
from ftm.websocket_client import run_main as client_main
from ftm.test_cloud import run_main as cloud_main

import subprocess, shlex
import multiprocessing
import time
import json

command = "python test.py"
def subprocess_cmd(command, cwd=None, **kwargs):
    if 'queue' in kwargs:
        queue = kwargs['queue']
    process = subprocess.Popen(command.split(), cwd=cwd, stdout=subprocess.PIPE)
    # output = process.stdout
    # error = process.stderr
    output, error = process.communicate()
    print(f"output: {output} \nerror: {error}")

# def subprocess_cmd(command):
#     process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
#     proc_stdout = process.communicate()[0].strip() 
#     print(proc_stdout)

# subprocess_cmd(command)

def procedure():
    queue = multiprocessing.Queue()
    cmd2 = "python server.py arg1 arg2 arg 3"
    classname = "Client"
    arguments = "/home/uday-vig/fault_tolerance_middleware/CloudSim_Conf"
    cmd3 = f'mvn exec:java -f CloudSimInterface/ -Dexec.mainClass={classname} -Dexec.args="{arguments}"'
    # cmd3 = f"mvn exec:java -Dexec.mainClass={classname} -Dexec.args={arguments}"
    cmd4 = "python websocket_client.py"
    # p1 = multiprocessing.Process(target=subprocess_cmd, args=(cmd2, "../"))
    # p2 = multiprocessing.Process(target=subprocess_cmd, args=(cmd3,))
    # p3 = multiprocessing.Process(target=subprocess_cmd, args=(cmd4, "../"))
    p1 = multiprocessing.Process(target=server_main)
    p2 = multiprocessing.Process(target=cloud_main)
    p3 = multiprocessing.Process(target=client_main, args=(queue,))
    
    p1.start()  #starting server
    time.sleep(2)
    p2.start()  #starting cloud
    time.sleep(4)
    p3.start()  #starting client
    p1.join()
    queue.put("quit")
    print("p1 finished")
    p2.join()
    p3.join()

def run_main():
    NUM_SIMULATION = 1
    EPOCH = 1
    NUM_LOCATIONS = 10
    output = "./results/default_output.pkl"

    THRESHOLD1 = 0.5
    THRESHOLD2 = 0.8
    SEED1 = 42
    SEED2 = 42
    SEED3 = 42

    fault_rate = (1 - THRESHOLD1) * (1 - THRESHOLD2) * NUM_LOCATIONS

    for iteration in range(NUM_SIMULATION):
        SEED2 = 42
        for epoch in range(EPOCH):
            print(f"Iteration: {iteration} | epoch: {epoch}")
            with open("ftm.conf") as handle:
                settings = json.load(handle)
            
            fault_rate = (1 - THRESHOLD1) * (1 - THRESHOLD2) * NUM_LOCATIONS
            settings['FAULT_RATE'] = fault_rate
            settings['EPOCH'] = epoch
            with open("ftm.conf", 'w') as handle:
                print(f"updating ftm.conf: {settings}")
                json.dump(settings, handle)

            cloud_args = f"{THRESHOLD1} {THRESHOLD2} {SEED1} {SEED2} {SEED3}"
            with open("CloudSim_Conf", 'w+t') as handle:
                print(f"updating CloudSim_Conf: {cloud_args}")
                handle.write(cloud_args)

            procedure()
            time.sleep(20)
            SEED1 += 1
            SEED2 += 1
            SEED3 += 1

        #updating the parameters
        THRESHOLD2 -= 0.05

if __name__ == '__main__':
    run_main()