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
        self.ser = serial.Serial(port=devpath, baudrate=self.baudrate, timeout=0)
        self.comms = {"aim": '\x01',
                      "fire": '\x02',
                      "GO": 'GO'}
        self.infos = {"start": '\x80',
                      "bad command": '\xE0',
                      "bad shooter": '\xE1',
                      "bad angle": '\xE2'}
        self.shooters = {"left": '\x01',
                         "center": '\x02',
                         "right": '\x03',
                         "error": '\x13'}
        self.read()

    def handle_message(self, msg, line):
        if msg == "start":
            print "~~~ HEARD SIGNAL TO START GAME ~~~"
            #TODO: signal to the main function that game started
        if msg == "bad command":
            print "invalid command ID"
        if msg == "bad shooter":
            print "recieved invalid shooter number"
        if msg == "bad angle":
            print str(line[:-2]) + "cannot fire at that angle"

    def send(self, data):
        # arbitrary data to board
        print "sending " + str(data)
        self.ser.write(data)

    def read(self):
        #line = self.ser.readline()[:-1] # strip newline
        #for msg, val in self.infos.iteritems():
        #    if val in line:
        #        handle_message(msg, line)
        #print "\t READ: " + line
        pass

    def aim(self, shooter, angle):
        data = self.comms["GO"] + self.comms["aim"] + self.shooters[shooter] + angle
        print "\ttrying to aim " + str(shooter) + " AT " + str(angle)
        self.ser.write(data)
        self.read()

    def fire(self, shooter):
        data = self.comms["GO"] + self.comms["fire"] + self.shooters[shooter]
        print "\ttrying to fire " + str(shooter)
        self.ser.write(data)
        self.read()

class FakeArduino:
    # for testing purposes
    def __init__(self):
        print "THIS IS NOT THE ARDUINO YOU ARE LOOKING FOR"
        print "~~~~~~~~ Initializing FakeArduino ~~~~~~~~~"
        self.comms = {"aim": bin(1),
                      "fire": bin(2),
                      "GO": bin(ord('G')) + bin(ord('O'))}
        self.infos = {"start": bin(80)}

    def send(self, data):
        print "FakeArduino thinks it's sending: " + str(data)

    def read(self):
        print "Read an imaginary line from FakeArduino"

    def aim(self, shooter, angle):
        print self.comms["GO"] + self.comms["aim"] + shooter + angle

    def fire(self, shooter):
        print self.comms["GO"] + self.comms["fire"] + shooter

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
