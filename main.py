#! /usr/bin/env python

import cv2
import sys

from shooters import Shooter
from arduino import Arduino, FakeArduino
from camera import Camera

def choose_center(centers):
    if centers == []:
        return centers
    nearesty = sorted(centers, key = lambda pair: pair[0])
    # game tactics logic goes here
    return nearesty[0]

def tactical_shoot(shooters, centers):
    # BB-conservation logic goes here
    target = choose_center(centers)
    if target:
        for s in shooters:
            if s.can_hit(target):
                s.shoot(target)
            else:
                s.aim(target)

def setup_shooters(board, offset_in = 3, field = [22.3125, 45], dpi = 17):
    offset = offset_in * dpi
    wpx = field[0] * dpi
    sixth = int(wpx / 6)
    # left shooter centered in first third of board
    left_shooter = Shooter(offset, sixth, dpi, board, "left")
    # center shooter centered
    center_shooter = Shooter(offset, int(wpx / 2), dpi, board, "center") 
    # right shooter centered in rightmost third of board
    right_shooter = Shooter(offset, (wpx - sixth), dpi, board, "right")
    shooterlist = [left_shooter, center_shooter, right_shooter]
    return shooterlist

def main(args):
    if "fake" in args:
        board = FakeArduino()
    else:
        board = Arduino()
    cam = Camera()
    cam.calibrate()
    #cam.adj_thresh(2, 50)
    shooterlist = setup_shooters(board, field = cam.board_size, dpi = cam.dpi)
    while True:
        targets = cam.get_targets()
        tactical_shoot(shooterlist, targets)
        aims = [s.get_aim_line() for s in shooterlist]
        cam.display(aims) 
        if (cv2.waitKey(2) >= 0):
            break
    cam.cleanup()

if __name__ == "__main__":
    main(sys.argv)
