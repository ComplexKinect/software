import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
from serial import Serial, SerialException
import io
import numpy as np
import time
import threading


def diffImg(t0, t1, t2):
  d1 = cv2.absdiff(t2, t1)
  d2 = cv2.absdiff(t1, t0)
  return cv2.bitwise_and(d1, d2)

def send_serial_msg(message):
    '''
    write the given message over serial
    '''
    cxn.write([int(message)])
    time.sleep(1)

def get_msg(section1, section2, section3):
    '''
    gets the integer message we want to send over serial which corresponds
    to which of the three sections has movement
    '''
    # motion in all sections
    if section1 and section2 and section3:
        msg = 7
    # motion in any two of the 3 sections
    elif section1 and section2:
        msg = 6
    elif section1 and section3:
        msg = 5
    elif section2 and section3:
        msg = 4
    # motion in any 1 of the sections
    elif section3:
        msg = 3
    elif section2:
        msg = 2
    elif section1:
        msg = 1
    else:
        msg = 0
    return msg

def start_serial_thread(message):
    '''
    function to start up and return the serial thread with the given message
    representing values for movement in 3 sections
    '''
    serial_thread = threading.Thread(name='serial',
                                     target=send_serial_msg,
                                     args=(message))
    try:
        serial_thread.start()
    except:
        print("unable to start thread")

    return serial_thread

def detect_motion(serial=False):
    if serial:
        PORT = '/dev/ttyACM1'
        cxn = Serial(PORT, baudrate=9600)

    camera = PiCamera()
#    camera.resolution = (320,240)
    rawCapture = PiRGBArray(camera)

    time.sleep(.1)

    winName = "Movement Indicator"
    t_minus = None
    t = None
    t_plus = None
    first = True

    for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        frame = f.array
        #Read three images first and crop each into 3 sections:
        #grab an image from the camera
        if t_minus is None:
            t_minus = frame
            cropped_tm = t_minus[:,:t_minus.shape[1]//3]
            cropped_tm2 = t_minus[:,t_minus.shape[1]//3:(2*t_minus.shape[1])//3]
            cropped_tm3 = t_minus[:,(2*t_minus.shape[1])//3:]
            rawCapture.truncate(0)
            continue
        elif t is None:
            t = frame
            cropped_t = t[:,:t.shape[1]//3]
            cropped_t2 = t[:,t.shape[1]//3:(2*t.shape[1])//3]
            cropped_t3 = t[:,(2*t.shape[1])//3:]
            rawCapture.truncate(0)
            continue
        elif t_plus is None:
            t_plus = frame
            cropped_tp = t_plus[:,:t_plus.shape[1]//3]
            cropped_tp2 = t_plus[:,t_plus.shape[1]//3:(2*t_plus.shape[1])//3]
            cropped_tp3 = t_plus[:,(2*t_plus.shape[1])//3:]
            rawCapture.truncate(0)
            images = [[cropped_tm, cropped_t, cropped_tp], [cropped_tm2, cropped_t2, cropped_tp2],
                  [cropped_tm3, cropped_t3, cropped_tp3]]
            continue

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
              if i == 0:
                  cropped = whole_image[:,:whole_image.shape[1]//3]
              elif i == 1:
                  cropped = whole_image[:,whole_image.shape[1]//3:(2*whole_image.shape[1])//3]
              elif i == 2:
                  cropped = whole_image[:,(2*whole_image.shape[1])//3:]
              images[i] = [t, t_plus, cropped]

        key = cv2.waitKey(10)
        if key == 27:
          cv2.destroyWindow("left pane")
          break
        #
        # cv2.putText(images[0][0], "{}".format(text), (10, 20),
        #   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        # print("im showing")
        rawCapture.truncate(0)

        cv2.imshow("left pane", images[0][0])
        cv2.imshow("middle pane", images[1][0])
        cv2.imshow("right pane", images[2][0])

    print( "Goodbye")

detect_motion()
