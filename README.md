# Complex Kinect Software

We are building a structure that responds to movement in front of it using opencv and a
camera mounted with a raspberry pi.

To use our code you must first install opencv and imutils.

To install opencv go to (this website)[https://sourceforge.net/projects/opencvlibrary/].
Extract the files to your choice of folder, and navigate to that folder.

To install imutils, run:
`pip3 install imutils`

Run the following commands:

`mkdir build`

ref`cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local ..`

`sudo make install`
