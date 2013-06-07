#! /usr/bin/env python

import cv2
import sys
import time

from shooters import Shooter
from arduino import Arduino, FakeArduino
from camera import Camera

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
            s.aim(target)
            if time.time() > s.last_shot + 1:
#            if s.can_hit(target):
#                s.shoot(target)
#            else:
                    s.fire()
"""
def differentiate(centers):
    # returns (larger, smaller) if 2 pucks else False
    if len(centers) != 2:
        return False
    if centers[0][2] > centers[1][2]:
        return (centers[0], centers[1])
    else:
        return (centers[1], centers[0])

def differentiate_shoot(shooters, centers):
    # find the two pucks or and 
    d = differentiate(centers)
    if d:
        triangle, star = d
    else:
        return
""" 

def setup_shooters(args, board, offset_in = 1, field = [22.3125, 45], dpi = 17):
    offset = int(offset_in * dpi)
    wpx = field[0] * dpi
    sixth = int(wpx / 6)
    # left shooter centered in first third of board
    left_shooter = Shooter(offset, 
                            sixth, 
                            dpi, 
                            board, 
                            "left", 
                            field = field, 
                            hit_default  = True, 
                            board_section = (0, (sixth * 2 - 1)), # in pixels
                            line_color = cv2.cv.RGB(255,0,0))
    # center shooter centered
    center_shooter = Shooter(offset, 
                            int(wpx / 2), 
                            dpi, 
                            board, 
                            "center", 
                            field = field, 
                            hit_default = True, 
                            board_section = ((sixth * 2), (sixth * 4 - 1)),
                            line_color = cv2.cv.RGB(0,0,255)) 
    # right shooter centered in rightmost third of board
    right_shooter = Shooter(offset, 
                            int(wpx - sixth), 
                            dpi, 
                            board, 
                            "right", 
                            field = field, 
                            hit_default = True,
                            board_section = (sixth * 4, field[0]),
                            line_color = cv2.cv.RGB(0,255,0))
    shooterlist = []
    if 'l' in args:
        shooterlist.append(left_shooter)
    if 'r' in args:
        shooterlist.append(right_shooter)
    if 'c' in args or shooterlist == []:
        shooterlist.append(center_shooter)
    return shooterlist

def main(args):
    if "fake" in args:
        board = FakeArduino()
    else:
        board = Arduino()
    cam = Camera()
    cam.calibrate()
    cam.adj_thresh(2, 10)
    shooterlist = setup_shooters(args, board, offset_in = 9.5, field = cam.board_size, dpi = cam.dpi)
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
