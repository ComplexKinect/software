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
import send_serial_msg, get_msg, start_serial_thread from send_message


def diffImg(t0, t1, t2):
  d1 = cv2.absdiff(t2, t1)
  d2 = cv2.absdiff(t1, t0)
  return cv2.bitwise_and(d1, d2)

def detect_motion(serial=False):
    if serial:
        PORT = '/dev/ttyACM1'
        cxn = Serial(PORT, baudrate=9600)

    camera = PiCamera()
    rawCapture = PiRGBArray(camera)

    time.sleep(.1)

    winName = "Movement Indicator"
    t_minus = None
    t = None
    t_plus = None
    first = True

    for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        frame = f.array
        # Read three images first and crop each into 3 sections:
        # Grab an image from the camera

        def return_cropped_list(t,num_frames):
            images = []
            for i in range(num_frames):
                images.append(crop_image(t,i,num_frames))
            rawCapture.truncate(0)    #resets camera
            return images

        def crop_image(t,frame,num_frames):
            '''t = image to crop
            pane = which pane (left, middle, right)
            num_panes = number of panes to crop into'''

            cropped = t[:,t.shape[1]*frame//num_frames:t.shape[1]*frame+1//num_frames]   # all vertical values, horizontal values from edge to edge
            return cropped

        if t_minus is None:
            t_minus = frame
            cropped_tm1,cropped_tm2,cropped_tm3 = return_cropped_list(t_minus,3)
            continue
        if t is None:
            t = frame
            cropped_t1,cropped_t2,cropped_t3 = return_cropped_list(t,3)
            continue
        if t_plus is None:
            t_plus = frame
            cropped_tp1,cropped_tp2,cropped_tp3 = return_cropped_list(t_plus,3)
            images = [[cropped_tm1, cropped_t1, cropped_tp1], [cropped_tm2, cropped_t2, cropped_tp2],
                  [cropped_tm3, cropped_t3, cropped_tp3]]
            continue

        for i, t_list in enumerate(images):
              section1 = False
              section2 = False
              section3 = False
              t_minus, t, t_plus = t_list
              movement = diffImg(t_minus, t, t_plus)
              movement = cv2.cvtColor(movement, cv2.COLOR_BGR2GRAY)
              # make everything greater than 10 white and less black (binary black or white)
              thresh = cv2.threshold(movement, 10, 255, cv2.THRESH_BINARY)[1]

              # dilate the thresholded image to fill in holes, then find contours on thresholded image
              thresh = cv2.dilate(thresh, None, iterations=2)
              _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

              # loop over the contours
              for c in cnts:
                  # if the contour is too small, ignore it
                  if cv2.contourArea(c) < 1000:
                      continue

                  # draw the contours
                  cv2.drawContours(t, c, -1, (0, 255, 0), 2)

                  if i == 0:
                      section1 = True
                      print('sees left')
                  if i== 1:
                      section2 = True
                      print('sees middle')
                  if i == 2:
                      section3 = True
                      print('sees right')

              if serial:
                  message = get_msg(section1, section2, section3)
                  if first:
                      first = False
                      serial_thread = start_serial_thread(message)
                  else:
                      if serial_thread.isAlive():
                          pass
                      else:
                          serial_thread = start_serial_thread(message)

              # Read next image
              whole_image = f.array
              cropped = crop_image(whole_image,i,3)
              images[i] = [t, t_plus, cropped]

        key = cv2.waitKey(10)
        if key == 27:             # escape key
          cv2.destroyWindow("left pane") #not sure why necessary but everything breaks without it
          break

        rawCapture.truncate(0)

        cv2.imshow("left pane", images[0][0])
        cv2.imshow("middle pane", images[1][0])
        cv2.imshow("right pane", images[2][0])

    print( "Goodbye")


if __name__ == '__main__':
    detect_motion()
