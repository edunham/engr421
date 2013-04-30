#! /usr/bin/env python

class shooter:
    def __init__(self, offset, xpos):
        self.offset = offset # :t offset Inches
        self.xpos = xpos
        self.aim = 128
    def can_hit(target):
        return True

LeftShooter = shooter(3, 8)
CenterSooter = shooter(3, 12) 
RightShooter = shooter(3, 16)

