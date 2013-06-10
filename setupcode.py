#! /usr/bin/env python

import cv2

from shooters import Shooter

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
    print shooterlist
    return shooterlist

