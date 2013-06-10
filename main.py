#! /usr/bin/env python

import cv2
import sys
import time

from arduino import Arduino, FakeArduino, SerialCommander
from camera import Camera
from field import Field
from setupcode import *

def choose_center(centers):
    if centers == []:
        return centers
    nearesty = sorted(centers, key = lambda pair: pair[1], reverse=True)
    # game tactics logic goes here
    return nearesty[0]

def tactical_shoot(shooters, centers):
    # BB-conservation logic goes here
    target = choose_center(centers)
    if target:
        for s in shooters:
#            if time.time() > s.last_shot + 1:
#            if s.can_hit(target):
            s.shoot(target)
#            else:
#                    s.fire()

def main(args):
    if "fake" in args:
        board = FakeArduino()
    else:
        board = Arduino()
    cam = Camera()
    cam.calibrate()
    #cam.adj_thresh(2, 10)
    shooterlist = setup_shooters(args, board, offset_in = 9.5, field = cam.board_size, dpi = cam.dpi)
    if "old" in args:
        print "using old program"
        while True:
            targets = cam.get_targets()
            print targets
            tactical_shoot(shooterlist, targets)
            aims = [s.get_aim_line() for s in shooterlist]
            cam.display(aims) 
            if (cv2.waitKey(2) >= 0):
                break
    if "fail" in args:
        print "using test program"
        while True:
            targets = cam.get_targets()
            for s in shooterlist:
                for t in targets:
                    s.shoot(t)
            aims = [s.get_aim_line() for s in shooterlist]
            cam.display(aims)
            if cv2.waitKey(2) >= 0:
                break
    elif "new" in args:
        print "using new program"
        field = Field()
        care = True # try to shoot after failmax fails?
        fails = 0
        failmax = 10
        while True:
            pucks = cam.get_pucks()
            if not pucks:
                pucks = (cam.get_one())
            if not pucks:
                if care:
                    fails += 1
                    if fails > failmax:
                        fails = 0
                        pucks = cam.get_targets()
                        pucks = (pucks[0], pucks[1])
                    else:
                        continue
                else:continue
            elif care:
                fails = 0
            field.update_pucks(pucks)
            target = field.get_best_target_pos()
            for s in shooterlist:
                if s.can_hit(target):
                    s.shoot(target)
            aims = [s.get_aim_line() for s in shooterlist]
            cam.display(aims)
            if cv2.waitKey(2) >= 0:
                break
    cam.cleanup()

if __name__ == "__main__":
    main(sys.argv)
