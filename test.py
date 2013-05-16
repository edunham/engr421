#!/usr/bin/env python

from arduino import Arduino
import sys

def shots(board):
    shooters = ["left", "center", "right"]
    aims = [bin(10), bin(20), bin(80), bin(100)]
    for s in shooters:
        for a in aims:
            board.aim(s, a)
            board.read()
    for s in shooters:
        board.fire(s)
        board.read()

def errors(board):
    bad_angle = '\x85'
    good_angle = '\x40'
    bad_shooter = "error"
    good_shooter = "center"
    print "aiming error shooter"
    board.aim(bad_shooter, good_angle)
    board.read()
    board.read()
    print "aiming center to bad angle"
    board.aim(good_shooter, bad_angle)
    board.read()
    print "firing error shooter"
    board.fire(bad_shooter)
    board.read()

def shooter(board):
    name = ''
    chosen = False
    shooters = ["left", "center", "right"]
    while not chosen:
        name = raw_input("which shooter? ")
        if name in shooters:
            chosen = True
            print "Using shooter " + name
        else:
            print name + " is not a valid shooter. Use one from "
            print shooters
    while True:
        angle = raw_input("aim to angle: ")
        board.aim(name, angle)
        board.read()
        board.read()
        board.read()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "USAGE: invoke with the name of the test you'd like to run."
        print "\t tests available: shots, errors, shooter"
    board = Arduino()
    board.read()
    if "shots" in sys.argv:
        print "TESTING: Taking some shots:"
        shots(board)
    if "errors" in sys.argv:
        print "TESTING: Inducing some errors:"
        errors(board)
    if "shooter" in sys.argv:
        print "TESTING: Interactive Shooter:"
        shooter(board)
    print "finished testing."
