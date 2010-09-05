import matplotlib.pyplot as plt

from mpl_toolkits.axes_grid.axislines import SubplotZero
from collections import deque
import sys
import json

def main():
    f = open("game_output.txt", "r")
    l = json.load(f)
    min_time = 0
    for val in l:
        if min_time == 0:
            min_time = val["time"]
        if val["time"] < min_time:
            min_time = val["time"]
    max_time = 0
    for val in l:
        if max_time == 0:
            max_time = val["time"]
        if val["time"] > max_time:
            max_time = val["time"]

    print "%s %s" % (min_time, max_time)

    fig = plt.figure(1)
    fig.subplots_adjust(right=0.85)
    ax = SubplotZero(fig, 1, 1, 1)
    fig.add_subplot(ax)

    # make right and top axis invisible
    ax.axis["right"].set_visible(False)
    ax.axis["top"].set_visible(False)

    # make xzero axis (horizontal axis line through y=0) visible.
    ax.axis["xzero"].set_visible(False)
    #ax.axis["xzero"].label.set_text("Axis Zero")

    ax.set_xlim(min_time, max_time)
    ax.set_ylim(0, 4)
    ax.set_xlabel("Time")
    ax.set_ylabel("HRV")

    # make new (right-side) yaxis, but wth some offset
    # offset = (20, 0)
    # new_axisline = ax.get_grid_helper().new_fixed_axis

    # ax.axis["right2"] = new_axisline(loc="right",
    #                                  offset=offset,
    #                                  axes=ax)
    # ax.axis["right2"].label.set_text("Label Y2")

    #ax.plot([-2,3,2])
    t_hrv = []
    hrv = []
    for val in l:
        if "hrv" in val.keys():
            t_hrv.append(val["time"])
            hrv.append(val["hrv"])
            #ax.plot(val["time"], val["hrv"], 'b,')
        elif "key" in val.keys():
            ax.plot(val["time"], 2.0, 'r,')
    ax.plot(t_hrv, hrv, 'b-')

    hrv_dict = []
    for el in l:
        try:
            hrv_dict.append((el["time"], el["hrv"]))
        except KeyError:
            pass

    peak_dict = []

    current_peak = 0
    hrv_window = deque()
    hrv_limit = 20
    hrv_total = []
    stop_counter = 0
    hrv_itr = hrv_dict.__iter__()
    b = hrv_itr.next()

    while 1:
        a = [b[0], b[1], 0]
        hrv_window.append(a)
        hrv_total.append(a)
        if len(hrv_window) > hrv_limit:
            hrv_window.popleft()
        max_hrv = 0
        max_time = 0
        for h in hrv_window:
            if h[1] > max_hrv:
                max_time = h[0]
                max_hrv = h[1]
        for h in hrv_window:
            if h[0] == max_time:
                h[2] = h[2] + 1
                break
        try:
            c = hrv_itr.next()
            b = c
        except StopIteration:
            stop_counter = stop_counter + 1
            if stop_counter == hrv_limit:
                break
            
    pulse = 0
    for (time, hrv, score) in hrv_total:
        if score > 17:
            pulse = pulse + 1
            ax.plot(time, hrv, 'g,')

    print "Pulse: %s" % (pulse)
        
    plt.draw()
    plt.show()

if __name__ == '__main__':
    sys.exit(main())
