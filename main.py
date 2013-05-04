#! /usr/bin/env python

import cv2
from shooters import Shooter
from arduino import Arduino
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
    Board = Arduino()
    left_shooter = Shooter(3, 8, 17, Board, bin(01))
    center_shooter = Shooter(3, 12, 17, Board, bin(02)) 
    right_shooter = Shooter(3, 16, 17, Board, bin(03))
    cam = Camera()
    shooterlist = [left_shooter, center_shooter, right_shooter]

    cam.calibrate()

    while True:
        targets = cam.get_targets()
        tactical_shoot(shooterlist, targets)
        cam.display(None) 
        if (cv2.waitKey(2) >= 0):
            break
    cam.cleanup()
