'''
Vicky McDermott, Peter Seger and Gracey Wilson
PoE: Team Complex Kinect
Fall 2017

This file tracks volume of sound in front of our structure using thinkdsp.
It records small audio segments and processes them to determine the largest
magnitude and frequency of sound that has been heard in the previous few seconds.
We make use of threading so that we are able to record and process sound
simultaneously. We then send a value to serial corresponding to the volume
or frequency of the sound being recorded.

The data sent over Serial monitor is then processed through Arduino code and
tells the corresponding motors to move, causing the nodes to move differently
with different levels of sound.
'''

import pyaudio
import wave
import time
import sound_processing.thinkdsp as thinkdsp
import sound_processing.thinkplot as thinkplot
import numpy as np
import threading
from serial import Serial, SerialException


def record_sound():
    '''Records a few seconds on audio and saves it to the tester.wav file.
    '''
    CHUNK = 2*1024
    FORMAT = pyaudio.paUInt8
    CHANNELS = 1
    RATE = 48000
    RECORD_SECONDS = 0.5
    WAVE_OUTPUT_FILENAME = "tester.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)


    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def process_sound(serial):
    '''Interprets the sound wave from the previous few seconds and sends an
    appropriate value to serial if specified.

    Args:
        serial - boolean representing whether this function should be run with
        serial messages
    '''
    if serial:
        PORT = '/dev/ttyACM1'
        cxn = Serial(PORT, baudrate=9600)

    sound = thinkdsp.read_wave('tester.wav')

    spectrum = sound.make_spectrum()

    wave = spectrum.make_wave()

    val = build_mag_output(spectrum.amps)
    if val != 0:
        print(int(val))
        if serial:
            cxn.write([int(val[:3])])
            cxn.write([int(val[3:])])

def build_freq_output(data):
    '''Determines what value to send over serial based on frequency of sound.

    Args:
        data - a list in which each entry represents the amplitude magnitude of
        the frequency at that index

    Returns:
        integer between 1 and 4 representing the frequency of the sound

    NOT CURRENTLY BEING CALLED
    '''
    maxmag = 0
    for i, d in enumerate(data):
        if d > maxmag:
            maxmag = d
            maxfreq = i
    if maxfreq < 200:
        return 1
    elif maxfreq >= 200 and maxfreq < 400:
        return 2
    elif maxfreq >= 400 and maxfreq < 600:
        return 3
    elif maxfreq >= 600:
        return 4

def build_mag_output(data):
    '''Determine what value to send over serial based on volume of sound.

    Args:
        data - a list in which each entry represents the amplitude magnitude of
        the frequency at that index

    Returns:
        string of 0s and 1s representing the volume of sound, which will
        correspond to how many panes to move in our Arduino code
    '''
    maxmag = 0
    for i, d in enumerate(data):
        if d > maxmag:
            if i >1000 and i<5000:
                maxmag = d
                maxfreq = i
    print(maxmag)
    if maxmag >= 600:
        return '111111'
    elif maxmag >= 500:
        return '111110'
    elif maxmag >= 400:
        return '011110'
    elif maxmag >= 300:
        return '001110'
    elif maxmag >= 100:
        return '001100'
    elif maxmag >= 25:
        return '000100'
    return '000000'

def detect_sound(serial=False):
    '''Starts the threading for processing and recording sound.

    Args:
        serial - (default False) boolean representing whether this function should
        be run with serial messages
    '''
    while True:
        record = threading.Thread(name='record', target=record_sound)
        process = threading.Thread(name='process', target=process_sound, args=(serial,))
        try:
            record.start()
            process.start()
        except:
            print("unable to start thread")
        record.join()
        process.join()

if __name__ == '__main__':
    detect_sound(True)
