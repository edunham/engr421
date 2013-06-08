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
        print "frameheight"
        cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 600);
        print "frame width"
        cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 800);
        
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
        self.puck_min_px = 100
        self.tsize = (int(self.board_size[0]*self.dpi), int(self.board_size[1]*self.dpi))
        self.tmat = None
        self.field_img = None
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
        self.field_img = cv2.warpPerspective(self.get_frame(), self.tmat, dsize = self.tsize)
        return self.field_img

    def get_bw(self):
        gray = cv2.cvtColor((self.get_field()), cv2.COLOR_RGB2GRAY)
        # cv2.threshold(src, thresh, maxval, type[, dst]) ->  retval, dst
        # dst - output array of the same size and type as src.
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
        for t in range(140, 200, 2):
            print "\t trying " + str(t)
            self.threshval = t
            if all((len(self.get_targets()) == pucks) for x in range(stability)):
                works.append(t)
        print "VALID THRESHOLDS: " + str(works)
        if works:
            self.threshval = works[0]
        else:
            self.threshval = old_thresh
        print "THRESHHOLD SET TO: " + str(self.threshval)
      
    def get_targets(self):
        centers = []
        (contours, hierarchy) = cv2.findContours(self.get_bw(), mode=cv2.cv.CV_RETR_EXTERNAL, method=cv2.cv.CV_CHAIN_APPROX_SIMPLE)
        for c in contours:
            moments = cv2.moments(c, True)
            if (len(filter(lambda x: x==0, moments.values())) > 0):# no divide by 0
                continue
            if cv2.contourArea(c) < self.puck_min_px:
                # reduce false positives
                continue
            #else:
            #    break
            center = (moments['m10']/moments['m00'], moments['m01']/moments['m00'])
            center = map(lambda x: int(round(x)), center) # float to integer
            #center.append(cv2.coutourArea(c)) # store puck size
            centers.append(center)
        self.targets = centers
        return centers

    def display(self, lines = None):
        cv2.imshow("RAW", self.raw_img)
        cv2.imshow("B&W", self.bw_img)
        output = self.field_img#self.new_rgb_image(self.tsize[0], self.tsize[1])
        linewidth = 2
        radius = 20
        for t in self.targets:
            print t
            cv2.circle(output, tuple(t), radius, cv2.cv.RGB(0,255,255), linewidth)
        if lines is not None:
            for l in lines:
                cv2.line(output, l.a, l.b, color = l.color, thickness = linewidth)
        cv2.imshow("RESULTS", output)

    def cleanup(self):
        cv2.destroyAllWindows()
        cv2.VideoCapture(self.dev_id).release()

