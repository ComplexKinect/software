# Complex Kinect Software

We are building a structure that responds to movement in front of it using OpenCV and a
camera mounted with a raspberry pi.

To use our code you must first install imutils, OpenCV and make opencv in order to make OpenCV operate effectively.

### Install imutils:
`pip3 install imutils`

### Install opencv:
Visit [this website](https://sourceforge.net/projects/opencvlibrary/), download
and extract the files to your choice of folder, and navigate to that folder.

### Install make opencv:
`mkdir build`

`cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local ..`

`sudo make install`
