#! /usr/bin/env python
import math

class Shooter:
    def __init__(self, offset, xpos, dpi, comms, n):
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

    def can_hit(self, target):
        return True

    def target2angle(self, target):
        opp = target[0] - self.xpospx
        adj = target[1] + self.offsetpx
        self.theta = self.centerdeg + math.degrees(math.atan(opp/adj))
        if self.theta <= self.leftdeg:
            self.theta = leftdeg
            return 1
        elif self.theta >= self.rightdeg:
            self.theta = rightdeg
            return 128
        else:
            return int((17.0/6) * self.theta)

    def get_aim_line(self, board_length, line_length = 30):
        angle = self.centerdeg - self.theta # + for cw of straight; - for ccw
        y1 = board_length
        # triangle not visible in img. adj is offset and opposite is where
        # barrel intersects line, since point where angle measured is pivot
        x1 = self.xpospx + int(math.tan(math.radians(angle))) * self.offsetpx
        # aim is hypotenuse of triangle on board, where near angle is 90 - angle
        # y is opposite from that and x is x1 + adjacent
        y2 = board_length - (int(math.sin(math.radians(90 - angle))) * line_length)
        x2 = x1 + (int(math.cos(math.radians(90 - angle))) * line_length)
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
