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

def print_duration(fault_rate, List, **kwargs):
    '''
    Args:
        fault_rate
    '''
    ax = kwargs.get('ax', None)
    label = kwargs.get('label', None)

    y = np.arange(1, len(List)+1, 1)
    mean_val = 0
    if ax is None:
        mean_val = np.array(List).mean()
        fig, ax = plt.subplots()
    if label is None:
        ax.plot(y, List)
    else:
        print("label passed")
        ax.plot(y, List, label=label)
    ax.set(xlabel='Epochs', ylabel='Availability', title=str(f"Fault Rate:{fault_rate} | Mean: {mean_val}"))
    ax.grid()

    # fig.savefig(f"fault_{fault_rate}_.png")
    if ax is label:
        plt.show()
    else:
        return ax

def print_timing(fault_rate, record, **kwargs):
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
    ax = kwargs.get('ax', None)
    label = kwargs.get('label', '')
    color = kwargs.get('color', 'red')
    
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
    if ax is None:
        fig, ax = plt.subplots()
    ax.plot(list(record.keys()), timing_mean, 'k-', label=label, color=color)
    ax.fill_between(list(record.keys()), timing_min, timing_max, color=color, alpha=0.3)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Num of Failures (cumulative)")
    ax.grid()
    if label is '':
        plt.show()
    else:
        return ax

def print_all_durations(data, **kwargs):
    ax = kwargs.get('ax', None)
    label = kwargs.get('label', '')
    color = kwargs.get('color', 'blue')

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
    if label != '':
        label += str(mean_val)

    # duration_mean.transpose

    # print(f"len data: {len(data.keys())} | type: {type(data.keys())} | shape: {np.array(data.keys()).shape()}")
    # print(f"data.keys(): {data.keys()}")
    # print(f"len mean: {len(duration_mean)}| type: {type(duration_mean)} | shape: {duration_mean.shape()}")
    # print(f"duration_mean: {duration_mean}")
    if ax is None:
        fig, ax = plt.subplots()
    ax.plot(list(data.keys()), duration_mean, 'k-', label=label, color=color)
    ax.fill_between(list(data.keys()), duration_min, duration_max, color=color, alpha=0.3)
    ax.set_xlabel("Fault rates")
    ax.set_ylabel("Availability")
    ax.set_title(f"Mean val: {mean_val}")
    ax.grid()
    if label is '':
        plt.show()
    else:
        return ax

def print_comparision(file1, file2):
    with open(file1, 'rb') as handle:
        result1 = pickle.load(handle)
    
    with open(file2, 'rb') as handle:
        result2 = pickle.load(handle)
    
    fig, axs = plt.subplots(len(result1.keys()), 2, figsize=(16, 30))
    
    i = 0
    for fault_rate1, fault_rate2 in zip(result1.keys(), result2.keys()):
        axs[i, 0] = print_duration(fault_rate1, result1[fault_rate1]['duration'], ax=axs[i, 0], label=f"new | mean:{np.array(result1[fault_rate1]['duration']).mean()}")
        axs[i, 0] = print_duration(fault_rate2, result2[fault_rate2]['duration'], ax=axs[i, 0], label=f"old | mean:{np.array(result2[fault_rate2]['duration']).mean()}")
        axs[i, 0].legend()

        axs[i, 1] = print_timing(fault_rate1, result1[fault_rate1]['timing'], ax=axs[i, 1], label=f"New", color='blue')
        axs[i, 1] = print_timing(fault_rate2, result2[fault_rate2]['timing'], ax=axs[i, 1], label=f"Old", color ='orange')
        axs[i, 1].legend()
        i += 1

    fig2, ax = plt.subplots(figsize=(18,40))
    ax = print_all_durations(result1, ax=ax, label="New", color='blue')
    ax = print_all_durations(result2, ax=ax, label="Old", color='orange')
    ax.legend()
    plt.show()
    
    # a = ScrollableWindow(fig)


def main():
    file1 = "OutputUday18.pkl"   #new
    file2 = "OutputUday19.pkl"   #old

    # with open(file1, 'rb') as handle:
    #     result = pickle.load(handle)

    # print(f"result: {json.dumps(result, indent=2)}")
    # print(f"result: {result}")
    #printing one simulation durations
    # for fault_rate, record in result.items():
    #     #displaying fault rate
    #     print("displaying")
    #     print_duration(fault_rate, record['duration'])

    #     print_timing(fault_rate, record['timing'])

    # print_all_durations(result)

    print_comparision(file1, file2)

main()
