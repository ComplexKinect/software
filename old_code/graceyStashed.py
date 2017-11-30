=======
    winName = "Movement Indicator"

    # Read three images first and crop each into 3 sections:
    data = np.fromstring(stream.getvalue(), dtype=np.uint8)
    image = cv2.imdecode(data, 1)
    def crop_image(image):
        crop1 = t_minus[:,:t_minus.shape[1]//3]
        crop2 = t_minus[:,t_minus.shape[1]//3:(2*t_minus.shape[1])//3]
        crop3 = t_minus[:,(2*t_minus.shape[1])//3:]
        return [image1,image2,image3]

    images = crop_image(image)
    for item in images:
        detect_face(item)

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
            sections = [section1,section2,section3]
            for section in sections:
                if serial:
                    if section:
                        cxn.write([int(sections[section+1])]) # write int(1 for section1, int(2) for section2, etc)

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
>>>>>>> Stashed changes
