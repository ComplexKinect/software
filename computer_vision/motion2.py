import cv2
import picamera
from picamera.array import PiRGBArray
from serial import Serial, SerialException
import io
import numpy as np
import time

def diffImg(t0, t1, t2):
  d1 = cv2.absdiff(t2, t1)
  d2 = cv2.absdiff(t1, t0)
  return cv2.bitwise_and(d1, d2)

def detect_motion(serial=False):
    if serial:
        PORT = '/dev/ttyACM1'
        cxn = Serial(PORT, baudrate=9600)

    camera = picamera.PiCamera()
    rawCapture = PiRGBArray(camera)

    time.sleep(.1)

    winName = "Movement Indicator"
    t_minus = None
    t = None
    t_plus = None

    for f in camera.capture_continuous(rawCapture, format="bgr"):
        frame = f.array
        # Read three images first and crop each into 3 sections:
        # grab an image from the camera
        if t_minus == None:
            t_minus = frame
            cropped_tm = t_minus[:,:t_minus.shape[1]//3]
            cropped_tm2 = t_minus[:,t_minus.shape[1]//3:(2*t_minus.shape[1])//3]
            cropped_tm3 = t_minus[:,(2*t_minus.shape[1])//3:]
            continue
        elif t == None:
            t = frame
            cropped_t = t[:,:t.shape[1]//3]
            cropped_t2 = t[:,t.shape[1]//3:(2*t.shape[1])//3]
            cropped_t3 = t[:,(2*t.shape[1])//3:]
            continue
        elif t_plus == None:
            t_plus = frame
            cropped_tp = t_plus[:,:t_plus.shape[1]//3]
            cropped_tp2 = t_plus[:,t_plus.shape[1]//3:(2*t_plus.shape[1])//3]
            cropped_tp3 = t_plus[:,(2*t_plus.shape[1])//3:]
            continue

        images = [[cropped_tm, cropped_t, cropped_tp], [cropped_tm2, cropped_t2, cropped_tp2],
                  [cropped_tm3, cropped_t3, cropped_tp3]]

        text = ""
        for i, t_list in enumerate(images):
              section1 = False
              section2 = False
              section3 = False
              t_minus, t, t_plus = t_list
              movement = diffImg(t_minus, t, t_plus)
              movement = cv2.cvtColor(movement, cv2.COLOR_BGR2GRAY) # not sure about RGB vs BGR?
              # make everything greater than 25 white and less black (binary black
              # or white)
              thresh = cv2.threshold(movement, 10, 255, cv2.THRESH_BINARY)[1]

              # dilate the thresholded image to fill in holes, then find contours
              # on thresholded image
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
                      if "left" not in text:
                          text += "left"
                          section1 = True
                          print('sees left')
                  if i== 1:
                      if "middle" not in text:
                          text += "middle"
                          section2 = True
                          print('sees middle')
                  if i == 2:
                      if "right" not in text:
                          text += "right"
                          section3 = True
                          print('sees right')

        if serial:
            if section1:
                cxn.write([int(11)])
            if section2:
                cxn.write([int(21)])
            if section3:
                cxn.write([int(31)])

        # Read next image
        print("hi")
        whole_image = f.array
        if i == 0:
          cropped = whole_image[:,:whole_image.shape[1]//3]
        elif i == 1:
          cropped = whole_image[:,whole_image.shape[1]//3:(2*whole_image.shape[1])//3]
        elif i == 2:
          cropped = whole_image[:,(2*whole_image.shape[1])//3:]
        images[i] = [t, t_plus, cropped]

        #key = cv2.waitKey(10)
        #if key == 27:
        #  cv2.destroyWindow(winName)
        #  break

        cv2.putText(images[0][0], "{}".format(text), (10, 20),
          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        print("im showing")
        cv2.imshow("left pane", f.array)
        rawCapture.truncate(0)
        #cv2.imshow("middle pane", images[1][0])
        #cv2.imshow("right pane", images[2][0])

    print( "Goodbye")

detect_motion()
