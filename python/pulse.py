from contextlib import contextmanager, closing
from lightstone import lightstone
import threading
import sys
import select
import json
import time

# UNIX
def getch():
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

class LightstoneRecorder(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = threading.Event()
        self.readings = []
        return

    def run(self):
        with closing(lightstone.open()) as l:
            while not self.stop.is_set():
                l.get_data()
                self.readings.append({"scl": l.scl, "hrv": l.hrv, "t": time.time()})
        print "Exiting Lightstone Thread"


class KeyRecorder(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = threading.Event()
        self.readings = []
        return

    def run(self):
        while not self.stop.is_set():
            getch()
            if not self.stop.is_set():
                self.readings.append({"key_time": time.time()})
        print "Exiting Key Thread"

class PulseGame:
    def __init__(self):
        return

    def stopGame(self):
        print "Stopping game"
        self.lt.stop.set()
        if self.lt.is_alive():
            self.lt.join()
        self.kt.stop.set()
        if self.kt.is_alive():
            self.kt.join()

    def runGame(self):
        # Try to initialize lightstone recording thread

        self.lt = LightstoneRecorder()

        # Try to initialize keyboard reading thread

        self.kt = KeyRecorder()

        # Wait for trigger key to start timer

        print "Hit enter to start timer"
        getch()
        
        print "Starting timer"
        # Run threads for 60 seconds
        tm = threading.Timer(2, self.stopGame)
        tm.start()
        self.lt.start()
        self.kt.start()
        time.sleep(3)

        # Combine and sort information from objects
        print self.lt.readings
        print self.kt.readings

        # Apply pulse peak algorithm

        # Apply scoring algorithm

        # Output to single json file

        # Show graph

        

def main():
    p = PulseGame()
    p.runGame()
    return 0

if __name__ == '__main__':
    sys.exit(main())


