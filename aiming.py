#! /usr/bin/env python

from puck_detector import *
from shooters import *


def choose_center(centers):
    nearesty = sorted(centers, key = lambda pair: pair[0])
    # game tactics logic goes here
    return nearesty[0]

def untan(o,a):
    return math.degrees(math.atan(o/a))

def deg2aim(deg):
    if deg <= 0:
        aim = 1
    elif deg > 90:
        aim = 128 
    else:
        aim = (17.0/6) * deg
    return aim

def aim_shooter(centers, shooter):
    deg = 45
    target = choose_center(centers) # target (x,y) 
    opp = target[0] - shooter.xpospx # opposite side of the triangle
    adj = target[1] + shooter.offsetpx # adjacent side to our angle 
    if opp == 0:
        deg = 45
    elif opp > 0: # puck right of shooter
        deg = 45 + untan(opp, adj)
    else:
        deg = 45 - untan(-opp, adj)
def draw_aim(aim, image):
    #for center in centers:
    #    cv2.circle(image, tuple(center), 20, cv2.cv.RGB(0,255,255), 2)
    pass


if __name__ == "__main__":
    cam_id=0
    dev = open_camera(cam_id)
    print "camera:"
    print dev
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
        print "click the intersection of the robot line and side of board"
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
            img = cv2.warpPerspective(img_orig, transform,
dsize=transform_size)
            # dsize is for calculations; hack things before the imshows if
            # necessary
            cv2.imshow("warped", img)
            
            img_gray = rgb_to_gray(img)
            (im_thresh, im_bw) = do_threshold(img_gray, thresh_val)
            cv2.imshow("thresh", im_bw)

            contours = find_contours(im_bw)
            centers = find_centers(contours)

            #aim = aim_shooter(centers, CenterShooter)

            results_image = new_rgb_image(transform_size[0],
transform_size[1])
            cv2.drawContours(results_image, contours, -1, cv2.cv.RGB(255,0,0),
2)

            draw_aim(aim, results_image)
            draw_centers(centers, results_image)
            cv2.imshow("results", results_image)

        else: # if we failed to capture (camera disconnected?), then quit
            break

        if (cv2.waitKey(2) >= 0):
            break

    cleanup(cam_id)
