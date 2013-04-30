#! /usr/bin/env python

class shooter:
    def __init__(self, offset, xpos, dpi):
        self.offsetin = offset
        self.offsetpx = offset * dpi
        self.xposin = xpos
        self.xpospx = xpos * dpi
        self.aim = 128
    def can_hit(target):
        return True

LeftShooter = shooter(3, 8, 17)
CenterSooter = shooter(3, 12, 17) 
RightShooter = shooter(3, 16, 17)

