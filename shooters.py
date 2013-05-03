#! /usr/bin/env python
from arduino.py import Ardiuno

class shooter:
    def __init__(self, offset, xpos, dpi, comms, n):
        self.offsetin = offset
        self.offsetpx = offset * dpi
        self.xposin = xpos
        self.xpospx = xpos * dpi

        self.leftdeg = 0
        self.centerdeg = 45
        self.rightdeg = 90

        self.aim = 128
        self.shot = 0
        self.comms = comms
        self.number = n

    def can_hit(self, target):
        return True

    def target2angle(target):
        opp = target[0] - self.xpospx
        adj = target[1] + self.offsetpx
        deg = self.centerdeg + math.degrees(math.atan(opp/adj))
        if deg <= self.leftdeg:
            return 1
        elif deg >= self.rightdeg:
            return 128
        else:
            return (17.0/6) * deg

    def aim(self, target):
        if self.can_hit(target):
            self.aim = target2angle(target)
            self.comms.aim(self.number, self.aim)

    def fire(self):
        self.comms.fire(self.number)

    def shoot(self, target):
        self.aim(target)
        self.fire()

Board = Arduino()
LeftShooter = shooter(3, 8, 17, Board, 0x01)
CenterSooter = shooter(3, 12, 17, Board, 0x02) 
RightShooter = shooter(3, 16, 17, Board, 0x03)

