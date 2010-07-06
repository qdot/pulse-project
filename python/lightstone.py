#!/usr/bin/env python

from contextlib import contextmanager, closing
import sys
import usb.core
import usb.util
import os
import re

class lightstone(object):
    # VID : PID
    LIGHTSTONE_ID_LIST = { 0x0483 : 0x0035, 0x14FA : 0x0001 }    


    def __init__(self):
        self.hrv = 0.0
        self.scl = 0.0
        self.dev = None
        self.rawMsg = None
        self.is_open = False

    @classmethod
    def open(cls):
        l = lightstone()
        l._open()
        return l

    def _open(self):
        for (vid, pid) in self.LIGHTSTONE_ID_LIST.items():
            self.dev = usb.core.find(idVendor=vid, idProduct=pid)
            if self.dev != None:                
                self.is_open = True
                return True
        sys.stderr.write("Cannot open device")
        return False

    @contextmanager
    def closing(self):
        #self.close()
        self.is_open = False

    def close(self):
        return
        # if self.dev != None and self.is_open:
        #     self.dev.close()
    
    def get_data(self):
        message_finished = False
        while not message_finished:
            # InputStruct = hid_interrupt_read(self.hid,0x81,0x8,10);            
            # if InputStruct[0] != HID_RET_SUCCESS:
            #     continue
            # InputReport = InputStruct[1]
            InputReport = self.dev.read(0x81, 0x8, 0, 10)
            for msg_index in range(1, InputReport[0] + 1):

                current_char = chr(InputReport[msg_index])
                if self.rawMsg is None and current_char != '<':
                    continue
                elif self.rawMsg is None:
                    self.rawMsg = ''
                if current_char != '\r' and current_char != '\n':
                    self.rawMsg += current_char
                elif current_char == '\n':
                    raw_re = re.compile("\<RAW\>(?P<scl>[0-9A-Fa-f]{4}) (?P<hrv>[0-9A-Fa-f]{4})\<\\\\RAW\>")
                    result = re.search(raw_re, self.rawMsg)
                    if result:
                        self.scl = int(result.group("scl"), 16) * .01
                        self.hrv = int(result.group("hrv"), 16) * .001
                    message_finished = True;
                    self.rawMsg = None
    
def main(argv = None):
    with closing(lightstone.open()) as l:
        try:
            while(1):
                if not l.is_open:
                    break
                l.get_data()
                print "%f %f" % (l.scl, l.hrv)
        except KeyboardInterrupt:
            print "Exiting"

if __name__ == '__main__':
    sys.exit(main())

