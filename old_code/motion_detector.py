import cv2
import time
import imutils
import datetime

def detect_motion():
    camera = cv2.VideoCapture(0)
    time.sleep(0.25)
    first_frames = [None, None, None]

    while True:
        # grab the current frame and initialize the occupied/unoccupied text
        (grabbed, frame) = camera.read()
        text = ""

        # if the frame could not be grabbed, then we have reached the end
        # of the video
        if not grabbed:
            print("not grabbed")
            break

        cropped_img = frame[:,:frame.shape[1]//3]
        cropped_img2 = frame[:,frame.shape[1]//3:(2*frame.shape[1])//3]
        cropped_img3 = frame[:,(2*frame.shape[1])//3:]

        cropped_imgs = [cropped_img, cropped_img2, cropped_img3]

        for i, frame in enumerate(cropped_imgs):
            first_frame = first_frames[i]
            # resize the frame, convert it to grayscale, and blur it
            frame = imutils.resize(frame, width=500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            # if the first frame is None, initialize it
            if first_frame is None:
                first_frame = gray
                first_frames[i] = first_frame
                continue

            # compute the absolute difference between the current frame and
            # first frame
            frameDelta = cv2.absdiff(first_frame, gray)
            # make everything greater than 25 white and less black (binary black
            # or white)
            thresh = cv2.threshold(frameDelta, 10, 255, cv2.THRESH_BINARY)[1]

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
                cv2.rectangle(cropped_imgs[i], (x, y), (x + w, y + h), (0, 255, 0), 2)
                if i == 0:
                    if "left" not in text:
                        text += "left"
                if i== 1:
                    if "middle" not in text:
                        text += "middle"
                if i == 2:
                    if "right" not in text:
                        text += "right"

        cv2.putText(cropped_img, "{}".format(text), (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)


        # show the frame and record if the user presses a key
        #cv2.imshow("Security Feed", frame)
        #cv2.imshow("Thresh", thresh)
        #cv2.imshow("Frame Delta", frameDelta)
        cv2.imshow("cropped image part 1", cropped_img)
        cv2.imshow("cropped image part 2", cropped_img2)
        cv2.imshow("cropped image part 3", cropped_img3)


        key = cv2.waitKey(1) & 0xFF

        # if the `q` key is pressed, break from the loop
        if key == ord("q"):
            break

    # cleanup the camera and close any open windows
    camera.release()
    cv2.destroyAllWindows()


detect_motion()
