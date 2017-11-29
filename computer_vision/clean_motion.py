'''
Vicky McDermott and Gracey Wilson
PoE: Team Complex Kinect
Fall 2017

This file tracks motion in front of our structure using OpenCV.
It captures images, divides those images into panes, and tracks which panes
contain motion at a given time. Depending on which panes contain motion, a
different set of values is sent to Serial monitor via the functions we import
from send_message.py.

The data sent over Serial monitor is then processed through Arduino code and
tells the corresponding motors to move, causing the nodes in the corresponding
panels to open and close.
'''

import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
from serial import Serial, SerialException
import io
import numpy as np
import time
import threading
from send_message import send_serial_msg, get_msg, start_serial_thread


def diffImg(t0, t1, t2):
    '''Takes the difference of 3 images

    Args:
        t0 - first image in time to be differenced
        t1 - sescond image in time
        t2 - image from the most recent time

    Returns:
        an image array which is the conjunction of the difference of the
        first two images and the difference of the second two images
    '''
    d1 = cv2.absdiff(t2, t1)
    d2 = cv2.absdiff(t1, t0)
    return cv2.bitwise_and(d1, d2)

def return_cropped_list(t, num_frames, rawCapture):
    '''Takes an image and a number of frames, crops the image into the given
    number of frames, and returns a list of the cropped images that make up
    the larger image

    Args:
        t - the image to be cropped
        num_frames - number of frames the image should be cropped into

    Returns:
        a list of cropped images that make up the given image
    '''
    images = []
    for i in range(num_frames):
        images.append(crop_image(t, i, num_frames))
    rawCapture.truncate(0)    #resets camera
    return images

def crop_image(t, frame, num_frames):
    '''Takes an image, frame to get, and total number of frames the image is
    being split into and returns a single cropped section of an image.

    Args:
        t - image to crop
        pane - which pane (left, middle, right), represented by an integer
        from 0 to num_frames-1
        num_frames = number of frames to crop into

    Returns:
        an image array which is a cropped portion of the given image
    '''
    # all vertical values, horizontal values from edge to edge
    cropped = t[:,(t.shape[1]*frame)//num_frames:t.shape[1]*(frame+1)//num_frames]
    return cropped

def get_contours(image):
    '''Takes an image array and returns the contours found in that image array.

    Args:
        image - image array to find contours in

    Returns:
        list of contours in the given image
    '''
    # convert the image to black and white
    movement = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # make everything greater than 10 white and less black (binary black or white)
    thresh = cv2.threshold(movement, 10, 255, cv2.THRESH_BINARY)[1]

    # dilate the thresholded image to fill in holes, then find contours on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return cnts

def start_serial_tasks(serial_thread, first, section1, section2, section3):
    '''Constructs a message and starts the serial thread if it is not already
    running.

    Args:
        first: boolean representing whether this is the first time this function
        has been run
        section1: boolean representing motion in section 1
        section2: boolean representing motion in section 2
        section3: boolean representing motion in section 3

    Returns:
        the value of first after this function has been run (should always be false)
    '''
    message = get_msg(section1, section2, section3)
    if message != 0:
        if first:
            # the first time, start a serial thread with the message
            first = False
            serial_thread = start_serial_thread(message)
        else:
            # from then on check if the serial thread is alive and only
            # start a serial thread with the current message if one isn't
            # already running
            if serial_thread.isAlive():
                pass
            else:
                serial_thread = start_serial_thread(message)
    return serial_thread, first

def detect_motion(serial=False):
    '''Sets up the raspi camera to detect motion. Monitors for motion and sets
    up a video stream showing the cropped sections of the camera stream.

    Args:
        serial - (default False) boolean representing whether this function should
        be run with serial messages
    '''

    camera = PiCamera()
    rawCapture = PiRGBArray(camera)

    time.sleep(.1)

    t_minus = None
    t = None
    t_plus = None
    first = True
    serial_thread = None

    for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        frame = f.array
        # Read three images first and crop each into 3 sections:
        # Grab an image from the camera

        if t_minus is None:
            t_minus = frame
            cropped_tm1,cropped_tm2,cropped_tm3 = return_cropped_list(t_minus,3,rawCapture)
            continue
        if t is None:
            t = frame
            cropped_t1,cropped_t2,cropped_t3 = return_cropped_list(t,3,rawCapture)
            continue
        if t_plus is None:
            t_plus = frame
            cropped_tp1,cropped_tp2,cropped_tp3 = return_cropped_list(t_plus,3,rawCapture)
            images = [[cropped_tm1, cropped_t1, cropped_tp1], [cropped_tm2, cropped_t2, cropped_tp2],
                  [cropped_tm3, cropped_t3, cropped_tp3]]
            continue

        section1 = False
        section2 = False
        section3 = False
        for i, t_list in enumerate(images):
              
              t_minus, t, t_plus = t_list

              # take the difference of the past 3 images
              movement = diffImg(t_minus, t, t_plus)

              cnts = get_contours(movement)

              # loop over the contours
              for c in cnts:
                  # if the contour is too small, ignore it
                  if cv2.contourArea(c) < 1000:
                      continue

                  # draw the contours
                  cv2.drawContours(t, c, -1, (0, 255, 0), 2)

                  # determine which section each contour is in
                  if i == 0:
                      section1 = True
                      print('sees left')
                  if i== 1:
                      section2 = True
                      print('sees middle')
                  if i == 2:
                      section3 = True
                      print('sees right')

              # Read next image and shift images back one
              cropped = crop_image(frame,i,3)
              images[i] = [t, t_plus, cropped]

        if serial:
            serial_thread, first = start_serial_tasks(serial_thread, first, section1, section2, section3)

        # set it up to wait for the escape key to exit
        key = cv2.waitKey(10)
        # escape key
        if key == 27:
          cv2.destroyWindow("right pane")
          break

        # resets the camera
        rawCapture.truncate(0)

        # show the current 3 images
        cv2.imshow("left pane", images[0][0])
        cv2.imshow("middle pane", images[1][0])
        cv2.imshow("right pane", images[2][0])

    print( "Goodbye")

if __name__ == '__main__':
    detect_motion(True)
