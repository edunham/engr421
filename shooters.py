#! /usr/bin/env python
import math

class Shooter:
    def __init__(self, offset, xpos, dpi, comms, n, field = [22.3125, 45]):
        self.offsetin = offset
        self.offsetpx = offset * dpi
        self.xposin = xpos
        self.xpospx = xpos * dpi

        self.leftdeg = 0
        self.centerdeg = 45
        self.rightdeg = 90

        self.theta = 45
        self.aimval = 128
        self.shot = 0
        self.comms = comms
        self.number = n
        self.fieldpx = [field[0] * dpi, field[1] * dpi]

    def can_hit(self, target):
        return True 

    def target2angle(self, target):
        opp = target[0] - self.xpospx
        adj = target[1] + self.offsetpx
        self.theta = self.centerdeg + math.degrees(math.atan(opp/adj))
        if self.theta <= self.leftdeg:
            self.theta = self.leftdeg
            self.aimval = 1
        elif self.theta >= self.rightdeg:
            self.theta = self.rightdeg
            self.aimval = 128
        else:
            self.aimval = int((17.0/6) * self.theta)
        print "shooter " + self.number + " aimed at theta " + str(self.theta)
        return self.aimval

    def get_aim_line(self, line_length = 30):
        angle = self.centerdeg - self.theta # + for cw of straight; - for ccw
        print self.number + " in get_aim_line angle is " + str(angle)
        y1 = self.fieldpx[1]
        # triangle not visible in img. adj is offset and opposite is where
        # barrel intersects line, since point where angle measured is pivot
        x1add = int(round(math.tan(math.radians(angle)))) * self.offsetpx
        print "adding " + str(x1add) + " to x1"
        x1 = self.xpospx + x1add
        # aim is hypotenuse of triangle on board, where near angle is 90 - angle
        # y is opposite from that and x is x1 + adjacent
        y2sub = int(round(math.sin(math.radians(90 - angle)))) * line_length
        print "subtracting " + str(y2sub) + " from y2"
        y2 = self.fieldpx[1] - y2sub
        x2add = int(round(math.cos(math.radians(90 - angle)))) * line_length
        print "adding " + str(x2add) + " to x2"
        x2 = x1 + x2add 
        return ((x1, y1), (x2, y2))

    def aim(self, target):
        if self.can_hit(target):
            self.aimval = self.target2angle(target)
            self.comms.aim(self.number, bin(self.aimval))

    def fire(self):
        self.comms.fire(self.number)

    def shoot(self, target):
        self.aim(target)
        self.fire()
