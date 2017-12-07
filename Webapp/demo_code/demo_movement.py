'''
Gracey Wilson
PoE: Team Complex Kinect
Fall 2017

The data sent from this file over Serial monitor is then processed with
Arduino code and tells the corresponding motors to move, causing the nodes
in the corresponding panes of flowers to open and close.

This file does not require any sensor/camera input - it is a demo.

'''

from serial import Serial

def send_serial_msg(message):
    '''Write the given message over serial.

    Args:
        message - integer to be sent over serial
    '''
    print(message)
    PORT = '/dev/ttyACM0'
    cxn = Serial(PORT, baudrate=9600)
    cxn.write([int(message)])
    time.sleep(3)

def loop_msg(serial=True):
    '''Sends messages in fun pattern, no sensor or camera data used.'''

    while True:
        # Go across, adding 1 pane to those that move with each msg
        send_serial_msg('100000')
        send_serial_msg('110000')
        send_serial_msg('111000')
        send_serial_msg('111100')
        send_serial_msg('111110')
        send_serial_msg('111111')

        # Go across and make one pane move at a time
        send_serial_msg('100000')
        send_serial_msg('010000')
        send_serial_msg('001000')
        send_serial_msg('000100')
        send_serial_msg('000010')
        send_serial_msg('000001')

        # Start in middle and move out
        send_serial_msg('001100')
        send_serial_msg('011110')
        send_serial_msg('111111')


if __name__ == '__main__':
    loop_msg()
