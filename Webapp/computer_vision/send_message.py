'''
Vicky McDermott and Gracey Wilson
PoE: Team Complex Kinect
Fall 2017

This file sends a message to Serial monitor. It is called in clean_motion.py,
where the message is generated. Then our Arduino code tells the corresponding
motors on the structure to move.
'''

import threading
import time
from serial import Serial

def send_serial_msg(message):
    '''Write the given message over serial.

    Args:
        message - integer to be sent over serial
    '''
    print(message)
    PORT = '/dev/ttyACM0'
    cxn = Serial(PORT, baudrate=9600)
    cxn.write([int(message[:3])])    # CHANGED
    while cxn.out_waiting > 0:
        pass
    cxn.write([int(message[3:])])    # CHANGED
    time.sleep(1)

def get_msg(sections, num_frames):
    '''Gets the integer message we want to send over serial which corresponds
    to which of the three sections has movement.

    Args:
        sections: list of bools representing motion in each pane
        num_frames = number of frames the image has been cropped into

    Returns:
        string of 0s and 1s representing which sections have movement
    '''

    string_msg = ''
    for i in range(num_frames):
        if sections[i]:
            string_msg += '1'
        elif sections[i] == False:
            string_msg += '0'
    return string_msg

def start_serial_thread(message):
    '''Function to start up and return the serial thread with the given message
    representing values for movement in 3 sections.

    Args:
        message - integer value to be sent over serial

    Returns:
        the serial thread which has been started up with the given message
    '''
    serial_thread = threading.Thread(name='serial',
                                     target=send_serial_msg,
                                     args=(message,))
    try:
        serial_thread.start()
    except:
        print("unable to start thread")

    return serial_thread
