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
        self.tmat = None

    def get_frame(self):
        ret, img = self.device.read()
        if (ret == False): # failed to capture
            print >> sys.stderr, "Error capturing from video device."
            return None
        return img

    def new_rgb_image(self, width, height):
        image = numpy.zeros((height, width, 3), numpy.uint8)
        return image 

    def mouse_click_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print "Click at (%d,%d)" % (x,y)
            self.cornerpoints.append( (x,y) )

    def calibrate(self, board_size = [22.3125,45], dpi = 72, calib_file = None):
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
           
    def get_targets(self):
        centers = []
        (contours, hierarchy) = cv2.findContours(self.get_frame(), mode=cv2.cv.CV_RETR_EXTERNAL, method=cv2.cv.CV_CHAIN_APPROX_SIMPLE)
        for contour in contours:
            moments = cv2.moments(contour, True)
            if (len(filter(lambda x: x==0, moments.values())) > 0):# no divide by 0
                continue
            center = (moments['m10']/moments['m00'], moments['m01']/moments['m00'])
            center = map(lambda x: int(round(x)), center) # float to integer
            centers.append(center)
        return centers

    def cleanup(self):
        cv2.destroyAllWindows()
        cv2.VideoCapture(self.dev_id).release()

