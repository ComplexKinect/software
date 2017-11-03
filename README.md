# Complex Kinect Software

We are building a structure that responds to movement in front of it using opencv and a
camera mounted with a raspberry pi.

To use our code you need to install opencv and imutils.

`pip3 install imutils`

To install opencv go to this website <fill in website here>. Extract the files.
Cd to the folder where you have opencv.

`mkdir build`

`cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local ..`

`sudo make install`
