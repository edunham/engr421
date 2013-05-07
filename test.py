#!/usr/bin/env python

from arduino import Arduino


if __name__ == "__main__":
    board = Arduino()
    shooters = ["left", "center", "right"]
    aims = [bin(10), bin(20), bin(80), bin(100)]
    board.read()
    for s in shooters:
        for a in aims:
            board.aim(s, a)
            board.read()
    for s in shooters:
        board.fire(s)
        board.read()
