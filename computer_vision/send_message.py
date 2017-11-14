'''
Vicky McDermott and Gracey Wilson
PoE: Team Complex Kinect
Fall 2017

This file gets data about motion in front of our structure from clean_motion.py
and sends it to Serial monitor. Then our Arduino code tells the corresponding
motors on the structure to move.
'''

import cleanMotion.py

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
