import cv2
from picamera import PiCamera
from serial import Serial, SerialException
import io
import numpy as np

def diffImg(t0, t1, t2):
  d1 = cv2.absdiff(t2, t1)
  d2 = cv2.absdiff(t1, t0)
  return cv2.bitwise_and(d1, d2)

def detect_motion(serial=False):
    if serial:
        PORT = '/dev/ttyACM1'
        cxn = Serial(PORT, baudrate=9600)

    cam = picamera.PiCamera()
    # Create the in-memory stream
    stream = io.BytesIO()
    camera.start_preview()
    time.sleep(2)
    camera.capture(stream, format='jpeg')

    winName = "Movement Indicator"

    # Read three images first and crop each into 3 sections:
    data = np.fromstring(stream.getvalue(), dtype=np.uint8)
    t_minus = cv2.imdecode(data, 1)
    cropped_tm = t_minus[:,:t_minus.shape[1]//3]
    cropped_tm2 = t_minus[:,t_minus.shape[1]//3:(2*t_minus.shape[1])//3]
    cropped_tm3 = t_minus[:,(2*t_minus.shape[1])//3:]

    data = np.fromstring(stream.getvalue(), dtype=np.uint8)
    t = cv2.imdecode(data, 1)
    cropped_t = t[:,:t.shape[1]//3]
    cropped_t2 = t[:,t.shape[1]//3:(2*t.shape[1])//3]
    cropped_t3 = t[:,(2*t.shape[1])//3:]

    data = np.fromstring(stream.getvalue(), dtype=np.uint8)
    t_plus = cv2.imdecode(data, 1)
    cropped_tp = t_plus[:,:t_plus.shape[1]//3]
    cropped_tp2 = t_plus[:,t_plus.shape[1]//3:(2*t_plus.shape[1])//3]
    cropped_tp3 = t_plus[:,(2*t_plus.shape[1])//3:]

    images = [[cropped_tm, cropped_t, cropped_tp], [cropped_tm2, cropped_t2, cropped_tp2],
              [cropped_tm3, cropped_t3, cropped_tp3]]

    while True:
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
              if cv2.contourArea(c) < 500:
                  continue

              # draw the contours
              cv2.drawContours(t, c, -1, (0, 255, 0), 2)

              if i == 0:
                  if "left" not in text:
                      text += "left"
                      section1 = True
              if i== 1:
                  if "middle" not in text:
                      text += "middle"
                      section2 = True
              if i == 2:
                  if "right" not in text:
                      text += "right"
                      section3 = True

          if serial:
              if section1:
                  cxn.write([int(11)])
              if section2:
                  cxn.write([int(21)])
              if section3:
                  cxn.write([int(31)])

          # Read next image
          data = np.fromstring(stream.getvalue(), dtype=np.uint8)
          whole_image = cv2.imdecode(data, 1)
          if i == 0:
              cropped = whole_image[:,:whole_image.shape[1]//3]
          elif i == 1:
              cropped = whole_image[:,whole_image.shape[1]//3:(2*whole_image.shape[1])//3]
          elif i == 2:
              cropped = whole_image[:,(2*whole_image.shape[1])//3:]
          images[i] = [t, t_plus, cropped]

      key = cv2.waitKey(10)
      if key == 27:
        cv2.destroyWindow(winName)
        break

      cv2.putText(images[0][0], "{}".format(text), (10, 20),
          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
      cv2.imshow("left pane", images[0][0])
      cv2.imshow("middle pane", images[1][0])
      cv2.imshow("right pane", images[2][0])

    print( "Goodbye")

detect_motion()