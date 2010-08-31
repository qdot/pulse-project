import json
import sys
from collections import deque

def main():

    l = json.load(open("game_output.txt", "r"))
    hrv_dict = []
    for el in l: 
        try:
            hrv_dict.append((el["time"], el["hrv"]))
        except KeyError:
            pass

    peak_dict = []

    # print len(hrv_dict)
    # current_peak = 0
    # for (time, hrv) in hrv_dict:
    #     #print "%s %s" % (time, hrv)
    #     if hrv > current_peak:
    #         peak_dict.append((time, hrv))
    #         current_peak = hrv
    #     else:
    #         current_peak = current_peak * (1 - .0015)

    current_peak = 0
    hrv_window = deque()
    hrv_limit = 10
    hrv_total = []
    for (time, hrv) in hrv_dict:
        a = [time, hrv, 0]
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
                print h
                break

    print hrv_total
#    print peak_dict
    print len(peak_dict)

if __name__ == '__main__':
    sys.exit(main())
