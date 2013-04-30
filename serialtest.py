#! /usr/bin/env python
import serial

class Arduino:
    def __init__(self):
        self.baudrate = 9600
        self.devpath = '/dev/ttyACM0'
        self.ser = serial.Serial(self.devpath, self.baudrate)
        self.ser.readline()
    def send(self, data):
        self.ser.write(data)

    def read(self):
        print "read " + self.ser.readline()

if __name__ == "__main__":
    slave = Arduino()
    while True:
        data = raw_input(">")
        print "sending " + data + " to " + slave.devpath
        slave.send(data)
        slave.read()
        
