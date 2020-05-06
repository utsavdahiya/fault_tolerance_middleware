import matplotlib.pyplot as plt
import numpy as np
import pickle

def print_duration(fault_rate, List):
    '''
    Args:
        fault_rate
    '''
    y = np.arange(0.5, 1.0, 0.1)
    fig, ax = plt.subplots()
    ax.plot(y, List)
    ax.set(xlabel='Epochs', ylabel='Availability', title=str(fault_rate))
    ax.grid()

    fig.savefig(f"fault_{fault_rate}_.png")
    plt.show()

file_name = "default_ouput.pkl"

with open(file_name, 'rb') as handle:
    result = pickle.load(handle)

#printing one simulation durations
for fault_rate, record in result:
    #displaying fault rate
    print("displaying")
    print_duration(fault_rate, record['duration'])