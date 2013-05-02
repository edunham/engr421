#! /usr/bin/env python
import serial
import os

class Arduino:
    def __init__(self):
        self.baudrate = 9600
        if os.path.exists('/dev/ttyACM0'):
            devpath = '/dev/ttyACM0'
        elif os.path.exists('/dev/ttyACM1'):
            devpath = '/dev/ttyACM1'
        else:
            print "dude, plug in the Arduino"
            exit()
        self.ser = serial.Serial(port=devpath, baudrate=self.baudrate, timeout=1)
        self.ser.readline()
        self.commands = {"aim": 0x01,
                         "fire": 0x02}
        self.infos = {"start": 0x80}

    def send(self, data):
        # arbitrary data to board
        self.ser.write(data)

    def read(self):
        # read one line
        #TODO: check whether it's a code in infos 
        print "\t"+self.ser.readline()

    def aim(self, shooter, angle):
        data = 'GO' + self.commands["aim"] + shooter + angle
        print "AIMING " + shooter + " AT " + angle
        self.ser.write(data)

    def fire(self, shooter):
        data = 'GO' + self.commands["fire"] + shooter
        print "FIRING " + shooter

if __name__ == "__main__":
    slave = Arduino()
    while True:
        data = raw_input(">")
        if data:
            print "sending " + data + " to Arduino"
            slave.send(data)
        l = slave.ser.readline()
        while l:
            print l
            l = slave.ser.readline()
        
        
