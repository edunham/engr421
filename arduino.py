#! /usr/bin/env python
import serial

class Arduino:
    def __init__(self):
        self.baudrate = 9600
        self.devpath = '/dev/ttyACM1'
        self.ser = serial.Serial(port=self.devpath, baudrate=self.baudrate, timeout=1)
        self.ser.readline()
        self.commands = {"aim": 0x01,
                         "fire": 0x02}
        self.infos = {"start": 0x80}
    def send(self, data):
        self.ser.write(data)
    def read(self):
        print "read " + self.ser.readline()
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
            print "sending " + data + " to " + slave.devpath
            slave.send(data)
        l = slave.ser.readline()
        while l:
            print l
            l = slave.ser.readline()
        
        
