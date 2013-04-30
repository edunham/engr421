#!/usr/bin/python
#
# ENGR421 -- Applied Robotics, Spring 2013
# OpenCV Python Demo 
# Taj Morton <mortont@onid.orst.edu>
#

import sys
import cv2
import time
import numpy
import os

def open_camera(cam_id = 0):
    cap = cv2.VideoCapture(cam_id)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 600);
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 800);
    cap.set(cv2.cv.CV_CAP_PROP_FPS, 30);
    return cap


def get_frame(device):
    ret, img = device.read()
    if (ret == False): # failed to capture
        print >> sys.stderr, "Error capturing from video device."
        return None

    return img

def cleanup(cam_id = 0):
    cv2.destroyAllWindows()
    cv2.VideoCapture(cam_id).release()

def rgb_to_gray(img):
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

def do_threshold(image, threshold = 170):
    #(thresh, im_bw) = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    (thresh, im_bw) = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
    return (thresh, im_bw)

def find_contours(image):
    (contours, hierarchy) = cv2.findContours(image, mode=cv2.cv.CV_RETR_EXTERNAL, method=cv2.cv.CV_CHAIN_APPROX_SIMPLE)
    return contours

def find_centers(contours):
    centers = []
    for contour in contours:
        moments = cv2.moments(contour, True)

        # If any moment is 0, discard the entire contour. This is
        # to prevent division by zero.
        if (len(filter(lambda x: x==0, moments.values())) > 0): 
            continue

        center = (moments['m10']/moments['m00'] , moments['m01']/moments['m00'])

        # Convert floating point contour center into an integer so that
        # we can display it later.
        center = map(lambda x: int(round(x)), center)
        centers.append(center)

    return centers

def draw_centers(centers, image):
    for center in centers:
        cv2.circle(image, tuple(center), 20, cv2.cv.RGB(0,255,255), 2)

corner_point_list = []

def mouse_click_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print "Click at (%d,%d)" % (x,y)
        corner_point_list.append( (x,y) )

def get_transform_matrix(dev, board_size = [22.3125, 45], dpi = 72, calib_file = None):
    img = get_frame(dev)
    cv2.imshow("Calibrate", img)

    cv2.setMouseCallback("Calibrate", mouse_click_callback)

    while True:
        if (len(corner_point_list) >= 4):
            print "Got 4 points: "+str(corner_point_list)
            break

        if (cv2.waitKey(10) >= 0):
            break;

    cv2.destroyWindow("Calibrate")
    if (len(corner_point_list) >= 4):

        # do calibration
        src = numpy.array(corner_point_list, numpy.float32)
        dest = numpy.array( [ (0, 0), (0, board_size[1]*dpi), (board_size[0]*dpi, 0), (board_size[0]*dpi, board_size[1]*dpi) ], numpy.float32 )
        """
        coord stuff is where in the final image the clicked points end up,
being calc'd in inches for some damn reason. Divide by dpi for trigs.
        """
        trans = cv2.getPerspectiveTransform(src, dest)

        if calib_file:
            numpy.savetxt(calib_file, trans)
        
        return trans 
    else:
        return None

def new_rgb_image(width, height):
    image = numpy.zeros( (height, width, 3), numpy.uint8)
    return image

if __name__ == "__main__":
    cam_id=0
    dev = open_camera(cam_id)

    board_size = [22.3125, 45] # dimensions in inches of the part of the board
        # we care about -- measured robot line to robot line
    dpi = 17 # for all operations after skewing the image

    do_calibration = True
    calib_file = None

    if (len(sys.argv) > 1):
        calib_file = sys.argv[1]
        if os.path.exists(calib_file):
            do_calibration = False
        else:
            do_calibration = True

    if do_calibration:
        print "CALIBRATING:"
        print "top left, bottom left, top right, bottom right."
        transform = get_transform_matrix(dev, board_size, dpi, calib_file)
    else: # load calibration from file
        transform = numpy.loadtxt(calib_file)

    print transform

    transform_size = (int(board_size[0]*dpi), int(board_size[1]*dpi))
    def trackbar_fnc(val):
        global thresh_val
        thresh_val = val
    thresh_val = 220
    cv2.createTrackbar('threshhold', "thresh", thresh_val, 255, trackbar_fnc)
    while True:
        img_orig = get_frame(dev)
        if img_orig is not None: # if we did get an image
            cv2.imshow("video", img_orig)
            img = cv2.warpPerspective(img_orig, transform, dsize=transform_size)
            # dsize is for calculations; hack things before the imshows if
            # necessary
            cv2.imshow("warped", img)
            
            img_gray = rgb_to_gray(img)
            (im_thresh, im_bw) = do_threshold(img_gray, thresh_val)
            cv2.imshow("thresh", im_bw)

            contours = find_contours(im_bw)
            centers = find_centers(contours)

            results_image = new_rgb_image(transform_size[0], transform_size[1])
            cv2.drawContours(results_image, contours, -1, cv2.cv.RGB(255,0,0), 2)

            draw_centers(centers, results_image)
            cv2.imshow("results", results_image)

        else: # if we failed to capture (camera disconnected?), then quit
            break

        if (cv2.waitKey(2) >= 0):
            break

    cleanup(cam_id)
