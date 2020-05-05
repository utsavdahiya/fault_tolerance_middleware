import subprocess, shlex
import multiprocessing
import time

command = "python test.py"
def subprocess_cmd(command, cwd=None):
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

cmd2 = "python server.py arg1 arg2 arg 3"
cmd3 = "python websocket_client.py"
cmd4 = "python test_cloud.py"
p1 = multiprocessing.Process(target=subprocess_cmd, args=(cmd2, "../"))
p2 = multiprocessing.Process(target=subprocess_cmd, args=(cmd3, "../"))
p3 = multiprocessing.Process(target=subprocess_cmd, args=(cmd4, "../"))
p1.start()
time.sleep(2)
p3.start()
time.sleep(5)
p2.start()
p1.join()
print("p1 finished")