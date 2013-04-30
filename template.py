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
 
##
# Opens a video capture device with a resolution of 800x600
# at 30 FPS.
##
def open_camera(cam_id = 0):
    cap = cv2.VideoCapture(cam_id)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 600);
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 800);
    cap.set(cv2.cv.CV_CAP_PROP_FPS, 30);
    return cap
 
##
# Gets a frame from an open video device, or returns None
# if the capture could not be made.
##
def get_frame(device):
    ret, img = device.read()
    if (ret == False): # failed to capture
        print >> sys.stderr, "Error capturing from video device."
        return None
    return img
 
##
# Closes all OpenCV windows and releases video capture device
# before exit.
##
def cleanup(cam_id = 0): 
    cv2.destroyAllWindows()
    cv2.VideoCapture(cam_id).release()
 
##
# Creates a new RGB image of the specified size, initially
# filled with black.
##
def new_rgb_image(width, height):
    image = numpy.zeros( (height, width, 3), numpy.uint8)
    return image



########### Main Program ###########

if __name__ == "__main__":
    # Camera ID to read video from (numbered from 0)
    camera_id = 0
    dev = open_camera(camera_id) # open the camera as a video capture device
 
    while True:
        img_orig = get_frame(dev) # Get a frame from the camera
        if img_orig is not None: # if we did get an image
            cv2.imshow("video", img_orig) # display the image in a window named "video"
        else: # if we failed to capture (camera disconnected?), then quit
            break
 
        if (cv2.waitKey(2) >= 0): # If the user presses any key, exit the loop
            break
 
    cleanup(camera_id) # close video device and windows before we exit


"""
Image Thresholding:

A common way to simplify your computer vision problem is to convert your image into a black and white ("binary") image. The threshold used to decide what becomes black and what becomes white determines what features are ignored an which ones are important to your algorithm. Many thresholding algorithms expect the image input to be in grayscale. The following functions will take an image, convert it to grayscale, and then convert it to a binary image at the specified threshold. Be sure to include the functions from the template program (above) in here as well:
"""
##
# Converts an RGB image to grayscale, where each pixel
# now represents the intensity of the original image.
##
def rgb_to_gray(img):
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
 
##
# Converts an image into a binary image at the specified threshold.
# All pixels with a value <= threshold become 0, while
# pixels > threshold become 1
def do_threshold(image, threshold = 170):
    (thresh, im_bw) = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
    return (thresh, im_bw)



##################################################### 
# If you have captured a frame from your camera like in the template program above,
# you can create a bitmap from it as follows:
 
img_gray = rgb_to_gray(img_orig) # Convert img_orig from video camera from RGB to Grayscale
 
# Converts grayscale image to a binary image with a threshold value of 220. Any pixel with an
# intensity of <= 220 will be black, while any pixel with an intensity > 220 will be white:
(thresh, img_threshold) = do_threshold(img_gray, 220)
 
cv2.imshow("Grayscale", img_gray)
cv2.imshow("Threshold", img_threshold)

##
# Finds the outer contours of a binary image and returns a shape-approximation
# of them. Because we are only finding the outer contours, there is no object
# hierarchy returned.
##
def find_contours(image):
    (contours, hierarchy) = cv2.findContours(image,
mode=cv2.cv.CV_RETR_EXTERNAL, method=cv2.cv.CV_CHAIN_APPROX_SIMPLE)
    return contours



##################################################### 
# If you have created a binary image as above and stored it in "img_threshold"
# the following code will find the contours of your image:
contours = find_contours(img_threshold)
 
# Here, we are creating a new RBB image to display our results on
results_image = new_rgb_image(img_threshold.shape[1], img_threshold.shape[0])
cv2.drawContours(results_image, contours, -1, cv2.cv.RGB(255,0,0), 2)
 
# Display Results
cv2.imshow("results", results_image)

"""
Finding Centroids Of Contours:
Once you have found your contours, you may want to find the center of the
shape. OpenCV can accomplish this by finding the moments
(http://en.wikipedia.org/wiki/Image_moment) of your contour. The following
functions can be used to find and display the centroids of a list of contours:
"""
##
# Finds the centroids of a list of contours returned by
# the find_contours (or cv2.findContours) function.
# If any moment of the contour is 0, the centroid is not computed. Therefore
# the number of centroids returned by this function may be smaller than
# the number of contours passed in.
#
# The return value from this function is a list of (x,y) pairs, where each
# (x,y) pair denotes the center of a contour.
##
def find_centers(contours):
    centers = []
    for contour in contours:
        moments = cv2.moments(contour, True)
 
        # If any moment is 0, discard the entire contour. This is
        # to prevent division by zero.
        if (len(filter(lambda x: x==0, moments.values())) > 0): 
            continue
 
        center = (moments['m10']/moments['m00'] ,
moments['m01']/moments['m00'])
        # Convert floating point contour center into an integer so that
        # we can display it later.
 
        center = map(lambda x: int(round(x)), center)
        centers.append(center)
    return centers
 
##
# Draws circles on an image from a list of (x,y) tuples
# (like those returned from find_centers()). Circles are
# drawn with a radius of 20 px and a line width of 2 px.
##
def draw_centers(centers, image):
    for center in centers:
        cv2.circle(image, tuple(center), 20, cv2.cv.RGB(0,255,255), 2)
 


##################################################### 
# If you have computed the contours of your binary image as above
# and created an RGB image to show your algorithm's output, this will
# draw circles around each detected contour:
 
centers = find_centers(contours)
cv2.drawContours(results_image, contours, -1, cv2.cv.RGB(255,0,0), 2)
draw_centers(centers, results_image)
cv2.imshow("results", results_image)
# Global variable containing the 4 points selected by the user in the corners
# of the board
corner_point_list = []
 
##
# This function is called by OpenCV when the user clicks
# anywhere in a window displaying an image.
##
def mouse_click_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print "Click at (%d,%d)" % (x,y)
        corner_point_list.append( (x,y) )
 
##
# Computes a perspective transform matrix by capturing a single
# frame from a video source and displaying it to the user for
# corner selection.
#
# Parameters:
# * dev: Video Device (from open_camera())
# * board_size: A tuple/list with 2 elements containing the width and height
# (respectively) of the gameboard (in arbitrary units, like inches)
# * dpi: Scaling factor for elements of board_size
# * calib_file: Optional. If specified, the perspective transform matrix is
# saved under this filename.
#   This file can be loaded later to bypass the calibration step (assuming
#   nothing has moved).
##
def get_transform_matrix(dev, board_size, dpi, calib_file = None):
    # Read a frame from the video device
    img = get_frame(dev)
 
    # Displace image to user
    cv2.imshow("Calibrate", img)
 
    # Register the mouse callback on this window. When 
    # the user clicks anywhere in the "Calibrate" window,
    # the function mouse_click_callback() is called (defined above)
    cv2.setMouseCallback("Calibrate", mouse_click_callback)
 
    # Wait until the user has selected 4 points
    while True:
        # If the user has selected all 4 points, exit loop.
        if (len(corner_point_list) >= 4):
            print "Got 4 points: "+str(corner_point_list)
            break
 
        # If the user hits a key, exit loop, otherwise remain.
        if (cv2.waitKey(10) >= 0):
            break;
 
    # Close the calibration window:
    cv2.destroyWindow("Calibrate")
 
    # If the user selected 4 points
    if (len(corner_point_list) >= 4):
        # Do calibration
 
        # src is a list of 4 points on the original image selected by the user
        # in the order [TOP_LEFT, BOTTOM_LEFT, TOP_RIGHT, BOTTOM_RIGHT]
        src = numpy.array(corner_point_list, numpy.float32)
 
        # dest is a list of where these 4 points should be located on the
        # rectangular board (in the same order):
        dest = numpy.array( [ (0, 0), (0, board_size[1]*dpi),
(board_size[0]*dpi, 0), (board_size[0]*dpi, board_size[1]*dpi) ],
numpy.float32)
 
        # Calculate the perspective transform matrix
        trans = cv2.getPerspectiveTransform(src, dest)
 
        # If we were given a calibration filename, save this matrix to a file
        if calib_file:
            numpy.savetxt(calib_file, trans)
        return trans
    else:
        return None
 


##################################################### 
### Calibration Example ###
if __name__ == "__main__":
    cam_id = 0
    dev = open_camera(cam_id)
 
    # The size of the board in inches, measured between the two
    # robot boundaries:
    board_size = [22.3125, 45]
 
    # Number of pixels to display per inch in the final transformed image.
    # This
    # was selected somewhat arbitrarily (I chose 17 because it fit on my
    # screen):
    dpi = 17
 
    # Calculate the perspective transform matrix
    transform = get_transform_matrix(dev, board_size, dpi)
 
 
    # Size (in pixels) of the transformed image
    transform_size = (int(board_size[0]*dpi), int(board_size[1]*dpi))
    while True:
        img_orig = get_frame(dev)
        if img_orig is not None: # if we did get an image
            # Show the original (untransformed) image
            cv2.imshow("video", img_orig)
            
            # Apply the transformation matrix to skew the image and display it
            img = cv2.warpPerspective(img_orig, transform,
dsize=transform_size)
            cv2.imshow("warped", img)
 
        else: # if we failed to capture (camera disconnected?), then quit
            break
 
        if (cv2.waitKey(2) >= 0):
            break
 
    cleanup(cam_id)
