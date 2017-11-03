import cv2
# need to install picamera on raspi first
# from picamera import PiCamera
from serial import Serial, SerialException

PORT = '/dev/ttyACM1'
cxn = Serial(PORT, baudrate=9600)

def diffImg(t0, t1, t2):
  d1 = cv2.absdiff(t2, t1)
  d2 = cv2.absdiff(t1, t0)
  return cv2.bitwise_and(d1, d2)

def detect_motion():
    # cam = PiCamera()
    cam = cv2.VideoCapture(0)

    winName = "Movement Indicator"

    # Read three images first and crop each into 3 sections:
    t_minus = cam.read()[1]
    cropped_tm = t_minus[:,:t_minus.shape[1]//3]
    cropped_tm2 = t_minus[:,t_minus.shape[1]//3:(2*t_minus.shape[1])//3]
    cropped_tm3 = t_minus[:,(2*t_minus.shape[1])//3:]

    t = cam.read()[1]
    cropped_t = t[:,:t.shape[1]//3]
    cropped_t2 = t[:,t.shape[1]//3:(2*t.shape[1])//3]
    cropped_t3 = t[:,(2*t.shape[1])//3:]

    t_plus = cam.read()[1]
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
          movement = cv2.cvtColor(movement, cv2.COLOR_RGB2GRAY)
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

              #TODO this is where we will send serial msgs indicating which block motion is sensed in
              if i == 0:
                  if "left" not in text:
                      text += "left"
                      section1 = True
                      cxn.write([int(11)])
              if i== 1:
                  if "middle" not in text:
                      text += "middle"
                      section2 = True
                      cxn.write([int(21)])
              if i == 2:
                  if "right" not in text:
                      text += "right"
                      section3 = True
                      cxn.write([int(31)])

          if section1:
              cxn.write([int(11)])
          else:
              cxn.write([int(10)])
          if section2:
              cxn.write([int(21)])
          else:
              cxn.write([int(20)])
          if section3:
              cxn.write([int(31)])
          else:
              cxn.write([int(30)])
          # Read next image
          whole_image = cam.read()[1]
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
>>>>>>> bf1e17a10f134826884a6a17364dc8f114576997
