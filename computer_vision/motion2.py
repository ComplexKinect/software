import cv2

def diffImg(t0, t1, t2):
  d1 = cv2.absdiff(t2, t1)
  d2 = cv2.absdiff(t1, t0)
  return cv2.bitwise_and(d1, d2)

cam = cv2.VideoCapture(0)

winName = "Movement Indicator"

# Read three images first:
t_minus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
t = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
t_plus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)

while True:
  movement = diffImg(t_minus, t, t_plus)
  # make everything greater than 25 white and less black (binary black
  # or white)
  thresh = cv2.threshold(movement, 25, 255, cv2.THRESH_BINARY)[1]

  # dilate the thresholded image to fill in holes, then find contours
  # on thresholded image
  thresh = cv2.dilate(thresh, None, iterations=2)
  _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  # loop over the contours
  for c in cnts:
      # if the contour is too small, ignore it
      if cv2.contourArea(c) < 2000 or cv2.contourArea(c) > 30000:
          continue

      # compute the bounding box for the contour, draw it on the frame,
      # and update the text
      (x, y, w, h) = cv2.boundingRect(c)
      cv2.rectangle(t, (x, y), (x + w, y + h), (0, 255, 0), 2)
  cv2.imshow( winName, t)

  # Read next image
  t_minus = t
  t = t_plus
  t_plus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)

  key = cv2.waitKey(10)
  if key == 27:
    cv2.destroyWindow(winName)
    break

print( "Goodbye")
