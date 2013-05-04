#! /usr/bin/env python

import sys
import cv2
import time
import numpy
import os

class Camera:
    def __init__(self, cam_id = 0):
        # open the camera
        cap = cv2.VideoCapture(cam_id)
        cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 600);
        cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 800);
        cap.set(cv2.cv.CV_CAP_PROP_FPS, 30);
        
        self.dev_id = cam_id
        self.device = cap
        self.threshval = 170
        self.cornerpoints = []
        self.calibration_message = """
        CALIBRATING:
        top left, bottom left, top right, bottom right
        click the intersection between ROBOT LINE and BOARD EDGE
        """
        self.board_size = [22.3125, 45]
        self.dpi = 17
        self.tsize = (int(self.board_size[0]*self.dpi), int(self.board_size[1]*self.dpi))
        self.tmat = None
        self.raw_img = None
        self.bw_image = None
        self.targets = []

    def get_frame(self):
        ret, img = self.device.read()
        if (ret == False): # failed to capture
            print >> sys.stderr, "Error capturing from video device."
            return None
        self.raw_img = img
        return img 

    def get_field(self):
        return cv2.warpPerspective(self.get_frame(), self.tmat, dsize = self.tsize)
        
    def get_bw(self):
        gray = cv2.cvtColor((self.get_field()), cv2.COLOR_RGB2GRAY)
        (thr, bw) = cv2.threshold(gray, self.threshval, 255, cv2.THRESH_BINARY)
        self.bw_img = bw
        return bw

    def new_rgb_image(self, width, height):
        image = numpy.zeros((height, width, 3), numpy.uint8)
        return image 

    def mouse_click_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print "Click at (%d,%d)" % (x,y)
            self.cornerpoints.append( (x,y) )

    def calibrate(self, calib_file = None):
        board_size = self.board_size
        dpi = self.dpi
        img = self.get_frame()
        cv2.imshow("Calibrate", img)
        cv2.setMouseCallback("Calibrate", self.mouse_click_callback)
        print self.calibration_message
        while True:
            if (len(self.cornerpoints) >= 4):
                print "Got 4 points: "+str(self.cornerpoints)
                break
            if (cv2.waitKey(10) >= 0):
                break;
        cv2.destroyWindow("Calibrate")
        if (len(self.cornerpoints) >= 4):
            # do calibration
            src = numpy.array(self.cornerpoints, numpy.float32)
            dest = numpy.array( [ (0, 0), (0, board_size[1]*dpi), (board_size[0]*dpi, 0), (board_size[0]*dpi, board_size[1]*dpi) ], numpy.float32 )
            trans = cv2.getPerspectiveTransform(src, dest)
            self.tmat = trans

    def adj_thresh(self, pucks, stability = 10):
        # set self.threshval such that correct number of pucks show up for 
        # the number of consecutive frames set by stability
        old_thresh = self.threshval
        works = []
        print "auto-calibrating threshold..."
        for t in range(0, 255, 2):
            print "\t trying " + str(t)
            self.threshval = t
            if all((len(self.get_targets()) == pucks) for x in range(stability)):
                works.append(t)
        print "VALID THRESHOLDS: " + str(works)
        if works:
            self.threshval = works[len(works)/2]
        else:
            self.threshval = old_thresh
        print "THRESHHOLD SET TO: " + str(self.threshval)
      
    def get_targets(self):
        centers = []
        (contours, hierarchy) = cv2.findContours(self.get_bw(), mode=cv2.cv.CV_RETR_EXTERNAL, method=cv2.cv.CV_CHAIN_APPROX_SIMPLE)
        for contour in contours:
            moments = cv2.moments(contour, True)
            if (len(filter(lambda x: x==0, moments.values())) > 0):# no divide by 0
                continue
            center = (moments['m10']/moments['m00'], moments['m01']/moments['m00'])
            center = map(lambda x: int(round(x)), center) # float to integer
            centers.append(center)
        self.targets = centers
        return centers

    def display(self, lines = None):
        cv2.imshow("RAW", self.raw_img)
        cv2.imshow("B&W", self.bw_img)
        output = self.new_rgb_image(self.tsize[0], self.tsize[1])
        linewidth = 2
        radius = 20
        for t in self.targets:
            cv2.circle(output, tuple(t), radius, cv2.cv.RGB(0,255,255), linewidth)
        # for l in lines...TODO
        cv2.imshow("RESULTS", output)

    def cleanup(self):
        cv2.destroyAllWindows()
        cv2.VideoCapture(self.dev_id).release()

