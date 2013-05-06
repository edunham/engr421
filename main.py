#! /usr/bin/env python

import cv2
import sys

from shooters import Shooter
from arduino import Arduino, FakeArduino
from camera import Camera

def choose_center(centers):
    nearesty = sorted(centers, key = lambda pair: pair[0])
    # game tactics logic goes here
    return nearesty[0]

def tactical_shoot(shooters, centers):
    # BB-conservation logic goes here
    target = choose_center(centers)
    for s in shooters:
        if s.can_hit(target):
            s.shoot(target)
        else:
            s.aim(target)

if __name__ == "__main__":
    if "fake" in sys.argv:
        board = FakeArduino()
    else:
        board = Arduino()
    left_shooter = Shooter(3, 8, 17, board, bin(01))
    center_shooter = Shooter(3, 12, 17, board, bin(02)) 
    right_shooter = Shooter(3, 16, 17, board, bin(03))
    cam = Camera()
    shooterlist = [left_shooter, center_shooter, right_shooter]

    cam.calibrate()
    #cam.adj_thresh(2, 50)

    while True:
        targets = cam.get_targets()
        tactical_shoot(shooterlist, targets)
        aims = [s.get_aim_line() for s in shooterlist]
        cam.display(aims) 
        if (cv2.waitKey(2) >= 0):
            break
    cam.cleanup()
