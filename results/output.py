import matplotlib.pyplot as plt
import numpy as np
import pickle

def print_duration(fault_rate, List):
    '''
    Args:
        fault_rate
    '''
    y = np.arange(1, len(List)+1, 1)
    fig, ax = plt.subplots()
    ax.plot(y, List)
    ax.set(xlabel='Epochs', ylabel='Availability', title=str(fault_rate))
    ax.grid()

    fig.savefig(f"fault_{fault_rate}_.png")
    plt.show()

def print_all_durations(data):
    duration_mean = []
    duration_min = []
    duration_max = []

    for fault_rate, record in data:
        duration_mean.append(np.mean(data[fault_rate]['duration']))
        duration_max.append(np.max(data[fault_rate]['duration']))
        duration_min.append(np.min(data[fault_rate]['duration']))

    duration_mean = np.array(duration_mean)
    duration_max = np.array(duration_max)
    duration_min = np.array(duration_min)

    plt.figure()

def main():
    file_name = "default_output.pkl"

    with open(file_name, 'rb') as handle:
        result = pickle.load(handle)

    print(f"result: {result}")
    #printing one simulation durations
    for fault_rate, record in result:
        #displaying fault rate
        print("displaying")
        print_duration(fault_rate, record['duration'])

main()