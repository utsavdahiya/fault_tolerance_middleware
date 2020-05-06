import matplotlib.pyplot as plt
import numpy as np
import pickle
import json

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

    # fig.savefig(f"fault_{fault_rate}_.png")
    plt.show()

def print_all_durations(data):
    duration_mean = []
    duration_min = []
    duration_max = []

    for fault_rate, record in data.items():
        duration_mean.append(np.mean(record['duration']))
        duration_max.append(np.max(record['duration']))
        duration_min.append(np.min(record['duration']))

    duration_mean = np.array(duration_mean)
    duration_max = np.array(duration_max)
    duration_min = np.array(duration_min)

    print(f"data.keys(): {data.keys()}")
    print(f"duration_mean: {duration_mean}")
    plt.plot(data.keys(), duration_mean, 'k-')
    plt.fill_between(data.keys(), duration_min, duration_max, color='blue', alpha=0.2)
    plt.xlabel("Fault rates")
    plt.ylabel("Availability")
    plt.show()

def main():
    file_name = "default_output.pkl"

    with open(file_name, 'rb') as handle:
        result = pickle.load(handle)

    # print(f"result: {json.dumps(result, indent=2)}")
    print(f"result: {result}")
    #printing one simulation durations
    for fault_rate, record in result.items():
        #displaying fault rate
        print("displaying")
        print_duration(fault_rate, record['duration'])

    print_all_durations(result)

main()