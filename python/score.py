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
        m = max(hrv_window, key=lambda (x): x[1])
        m[2] = m[2] + 1
        # Move the iterator forward. If we're done iterating, just
        # readd the last element onto the end.
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
            pulse += 1
    print pulse

if __name__ == '__main__':
    sys.exit(main())
