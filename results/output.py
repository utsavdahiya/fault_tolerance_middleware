import matplotlib
import matplotlib.pyplot as plt
import numpy as numpy
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt
import numpy as np
import pickle
import json

class ScrollableWindow(QtWidgets.QMainWindow):
    def __init__(self, fig):
        self.qapp = QtWidgets.QApplication([])

        QtWidgets.QMainWindow.__init__(self)
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(QtWidgets.QVBoxLayout())
        self.widget.layout().setContentsMargins(0,0,0,0)
        self.widget.layout().setSpacing(0)

        self.fig = fig
        self.canvas = FigureCanvas(self.fig)
        self.canvas.draw()
        self.scroll = QtWidgets.QScrollArea(self.widget)
        self.scroll.setWidget(self.canvas)

        self.nav = NavigationToolbar(self.canvas, self.widget)
        self.widget.layout().addWidget(self.nav)
        self.widget.layout().addWidget(self.scroll)

        self.show()
        exit(self.qapp.exec_()) 


# create a figure and some subplots
# fig, axes = plt.subplots(ncols=4, nrows=5, figsize=(16,16))
# for ax in axes.flatten():
#     ax.plot([2,3,5,1])

# pass the figure to the custom window
# a = ScrollableWindow(fig)

def print_duration(fault_rate, List):
    '''
    Args:
        fault_rate
    '''
    mean_val = np.array(List).mean()
    y = np.arange(1, len(List)+1, 1)
    fig, ax = plt.subplots()
    ax.plot(y, List)
    ax.set(xlabel='Epochs', ylabel='Availability', title=str(f"Fault Rate:{fault_rate} | Mean: {mean_val}"))
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

    mean_val = duration_mean.mean()

    # duration_mean.transpose

    # print(f"len data: {len(data.keys())} | type: {type(data.keys())} | shape: {np.array(data.keys()).shape()}")
    print(f"data.keys(): {data.keys()}")
    # print(f"len mean: {len(duration_mean)}| type: {type(duration_mean)} | shape: {duration_mean.shape()}")
    print(f"duration_mean: {duration_mean}")
    plt.plot(list(data.keys()), duration_mean, 'k-')
    plt.fill_between(list(data.keys()), duration_min, duration_max, color='blue', alpha=0.3)
    plt.xlabel("Fault rates")
    plt.ylabel("Availability")
    plt.title(f"Mean val: {mean_val}")
    plt.grid()
    plt.show()

def print_comparision(file1, file2):
    with open(file1, 'rb') as handle:
        result1 = pickle.load(handle)
    
    with open(file2, 'rb') as handle:
        result2 = pickle.load(handle)
    
    fig, axs = plt.subplots(len(result1.keys()), 2, figsize=(16, 16))
    

def main():
    file1 = "output-simulation-2.pkl"
    file2 = "output-simulation-1.pkl"

    with open(file1, 'rb') as handle:
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

    print_comparision(file1, file2)

main()
