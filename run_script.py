from ftm.server import run_main as server_main
from ftm.websocket_client import run_main as client_main
from ftm.test_cloud import run_main as cloud_main

import subprocess, shlex
import multiprocessing
import time

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

def run_main():
    queue = multiprocessing.Queue()

    cmd2 = "python server.py arg1 arg2 arg 3"
    cmd3 = "python test_cloud.py"
    cmd4 = "python websocket_client.py"
    # p1 = multiprocessing.Process(target=subprocess_cmd, args=(cmd2, "../"))
    # p2 = multiprocessing.Process(target=subprocess_cmd, args=(cmd3, "../"))
    # p3 = multiprocessing.Process(target=subprocess_cmd, args=(cmd4, "../"))
    p1 = multiprocessing.Process(target=server_main)
    p2 = multiprocessing.Process(target=cloud_main)
    p3 = multiprocessing.Process(target=client_main, args=(queue,))
    p1.start()  #starting server
    time.sleep(2)
    p2.start()  #starting cloud
    time.sleep(5)
    p3.start()  #starting client
    p1.join()
    queue.put("quit")
    print("p1 finished")

if __name__ == '__main__':
    run_main()