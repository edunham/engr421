#! /usr/bin/env python
import math
import struct
import time
import cv2

"""
limits are currently set to 65 as max right and 115 as max left.
"""
class Line:
    def __init__(self, a, b, color):
        self.a = a  # (x,y)
        self.b = b  # (x,y)
        self.color = color #cv2.cv.RGB(255,255,255)
    def print_info(self):
        print "\tline from " + str(self.a) + " to " + str(self.b) + " color " + str(self.color)

class Shooter:
    def __init__(self, offset, xpos, dpi, comms, n, 
                 field = [22.3125, 45], 
                 hit_default = True, 
                 board_section = (0,10),
                 line_color = cv2.cv.RGB(0,255,255)
                 ):

        # how far back from the line is the pivot?
        self.offsetpx = offset
        # how far from the left side of the board is it?
        self.xpospx = xpos

        self.leftdeg = 115
        self.centerdeg = 90
        self.rightdeg = 65

        # (a,b) leftmost a and rightmost b where we're best to shoot, PX
        self.board_section = board_section

        self.theta = 45
        self.shots = 500
        self.seconds_between_shots = .5
        self.comms = comms
        self.number = n
        self.fieldpx = [field[0] * dpi, field[1] * dpi]
        self.hit_default = hit_default
        self.last_shot = time.time()
        self.line_color = line_color
        
    def can_hit(self, target):
        if self.shots > 0:
            if time.time() - self.seconds_between_shots > self.last_shot:
                return self.hit_default
        return False

    def target2angle(self, target):
        # y axis is upside-down :( (0,0) is TOP LEFT CORNER of image
        # servo pos means 115 is LEFT and 65 is RIGHT :/
        if not target:
            return self.theta
        opp = float(target[0] - self.xpospx)
        adj = float((self.fieldpx[1] - target[1]) + self.offsetpx)
        self.theta = self.centerdeg - math.degrees(math.atan(opp/adj))
        if self.theta >= self.leftdeg:
            self.theta = self.leftdeg
        elif self.theta <= self.rightdeg:
            self.theta = self.rightdeg
        # print "\tready to aim" + self.number + ' at ' + str(float(self.theta))
        return self.theta

    def get_aim_line(self, line_length = 500):
        #TODO: fix the fact that (0,0) is top left corner
        angle = self.theta - self.centerdeg # + for cw of straight; - for ccw
        y1 = self.fieldpx[1]
        # triangle not visible in img. adj is offset and opposite is where
        # barrel intersects line, since point where angle measured is pivot
        x1add = int((math.tan(math.radians(angle))) * self.offsetpx)
        x1 = self.xpospx + x1add
        # aim is hypotenuse of triangle on board, where near angle is 90 - angle
        # y is opposite from that and x is x1 + adjacent
        fix_round_error = .00001
        y2sub = int((math.cos(math.radians(angle)) + fix_round_error) * line_length)
        y2 = (self.fieldpx[1] - y2sub) + 2* self.offsetpx
        x2add = int((math.sin(math.radians(angle)) + fix_round_error) * line_length)
        x2 = x1 - x2add 
        return Line((x1, y1), (x2, y2), self.line_color)

    def aim(self, target):
        self.target2angle(target)
        self.comms.aim(self.number, struct.pack('B', (round((self.theta)))))

    def fire(self):
        self.comms.fire(self.number)
        self.last_shot = time.time()
        self.shots -= 1

    def shoot(self, target):
        self.aim(target)
        self.fire()
