ENGR421 Team 4, Spring 2013
===========================

Dean Reading -- Electrical

Emily Dunham -- Software

Minna O'Brien -- Mechanicla

Team [web site][site]

[site]:https://sites.google.com/site/engr421team4/

Laptop software
---------------

Vision code written and maintained by edunham unless marked otherwise.

All python code requires OpenCV libraries to run. 
ymmv with the versions in your package manger; my cv2.__version__ is Rev 4557

Arduino software
----------------

Arduino code written and maintained by Dean Reading unless marked otherwise. 

The .ino files require the Arduino IDE thing to run, which is named arduino 
and can be installed from one's package manager.

Wiring Notes
------------

Yellow is to 12V, red is to 5V. Do not plug it in backwards or the board will fry .

To Run Program
--------------

Calibrate the fixed values in Crossfire\_Program.ino such that the shooters
point straight ahead when the laptop sends them 90 degrees. Verify that they
don't fall off the board at max left and max right. Plug in all the wires to
the correct pins, determined by reading the Arduino program's source. 

Invoke main.py with l, c, and r for left, right, and center shooters -- give
it the letters of the ones you want in this game, separated by spaces. Also
indicate whether to use new or old strategy. If Arduino is not plugged in,
pass 'fake'. Thus: 

$ python main.py l c r new

will run it. On the still image, click top left, bottom left, top right, and
bottom right intersections between *robot line* and *edge of board*. Any
keystroke while the program is running will cause it to abort. 

If auto-threshholding is enabled (the cam.adj\_thresh() line in main.py isn't
commented out), the program will seek the best threshhold for detecting 2
pucks under the current lighting conditions. If lighting is uneven, try
lowering the second argument to adj\_thresh. If lighting is consistent across
the field, a higher stability value will be required. 
