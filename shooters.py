#! /usr/bin/env python
import math
import struct
import time

class Shooter:
    def __init__(self, offset, xpos, dpi, comms, n, 
                 field = [22.3125, 45], 
                 hit_default = True, 
                 board_section = (0,10)):

        # how far back from the line is the pivot?
        self.offsetpx = offset
        # how far from the left side of the board is it?
        self.xpospx = xpos

        self.leftdeg = 0
        self.centerdeg = 90
        self.rightdeg = 180

        # (a,b) leftmost a and rightmost b where we're best to shoot
        self.board_section = board_section

        self.theta = 45
        self.shot = 0
        self.comms = comms
        self.number = n
        self.fieldpx = [field[0] * dpi, field[1] * dpi]
        self.hit_default = hit_default
        self.last_shot = time.time()
        
    def can_hit(self, target):
        return self.hit_default

    def target2angle(self, target):
        # y axis is upside-down :( (0,0) is TOP LEFT CORNER of image
        opp = float(target[0] - self.xpospx)
        adj = float((self.fieldpx[1] - target[1]) + self.offsetpx)
        self.theta = self.centerdeg + math.degrees(math.atan(opp/adj))
        if self.theta <= self.leftdeg:
            self.theta = self.leftdeg
        elif self.theta >= self.rightdeg:
            self.theta = self.rightdeg
        print "\tready to aim" + self.number + ' at ' + str(float(self.theta))
        return self.theta

    def get_aim_line(self, line_length = 500):
        #TODO: fix the fact that (0,0) is top left corner
        angle = self.centerdeg - self.theta # + for cw of straight; - for ccw
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
        return ((x1, y1), (x2, y2))

    def aim(self, target):
        self.target2angle(target)
        self.comms.aim(self.number, struct.pack('B', (round((self.theta)))))

    def fire(self):
        self.comms.fire(self.number)
        self.last_shot = time.time()

    def shoot(self, target):
        self.aim(target)
        self.fire()
