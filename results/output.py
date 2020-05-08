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

def print_timing(fault_rate, record):
    '''
    Args:
        record : {
            0: [],
            1: [],
            .
            .
            SIMULATION_TIME: []
        }
    '''
    timing_mean = []
    timing_min = []
    timing_max = []

    for time, observations in record.items():
        timing_mean.append(np.mean(observations))
        timing_max.append(np.max(observations))
        timing_min.append(np.min(observations))

    timing_mean = np.array(timing_mean)
    timing_max = np.array(timing_max)
    timing_min = np.array(timing_min)

    y = np.arange(1)
    plt.plot(list(record.keys()), timing_mean, 'k-')
    plt.fill_between(list(record.keys()), timing_min, timing_max, color='red', alpha=0.3)
    plt.xlabel("Time (s)")
    plt.ylabel("Num of Failures (cumulative)")
    plt.grid()
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

    # duration_mean.transpose

    # print(f"len data: {len(data.keys())} | type: {type(data.keys())} | shape: {np.array(data.keys()).shape()}")
    print(f"data.keys(): {data.keys()}")
    # print(f"len mean: {len(duration_mean)}| type: {type(duration_mean)} | shape: {duration_mean.shape()}")
    print(f"duration_mean: {duration_mean}")
    plt.plot(list(data.keys()), duration_mean, 'k-')
    plt.fill_between(list(data.keys()), duration_min, duration_max, color='blue', alpha=0.3)
    plt.xlabel("Fault rates")
    plt.ylabel("Availability")
    plt.grid()
    plt.show()

def main():
    file_name = "output-simulation-1.pkl"

    with open(file_name, 'rb') as handle:
        result = pickle.load(handle)

    # print(f"result: {json.dumps(result, indent=2)}")
    print(f"result: {result}")
    #printing one simulation durations
    for fault_rate, record in result.items():
        #displaying fault rate
        print("displaying")
        print_duration(fault_rate, record['duration'])

        print_timing(fault_rate, record['timing'])

    print_all_durations(result)

main()
