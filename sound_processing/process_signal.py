import pyaudio
import wave
import time
import thinkdsp
import thinkplot
import numpy as np
import threading
from serial import Serial, SerialException

#PORT = '/dev/ttyACM1'
#cxn = Serial(PORT, baudrate=9600)

def record_sound():
    CHUNK = 1024
    # FORMAT = pyaudio.paInt16
    FORMAT = pyaudio.paUInt8
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 0.5
    WAVE_OUTPUT_FILENAME = "tester.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    # print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    # print("* done recording")
    # print(int.from_bytes(frames[0],byteorder='little'))

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def process_sound():
    # cos_sig = thinkdsp.CosSignal(freq=440, amp=1.0, offset=0)
    # sin_sig = thinkdsp.SinSignal(freq=880, amp=0.5, offset=0)
    # mix = sin_sig + cos_sig

    # wave = mix.make_wave(duration=0.5, start=0, framerate=11025)
    sound = thinkdsp.read_wave('tester.wav')
    # wave.write(filename='output.wav')
    # thinkdsp.play_wave(filename='input.wav',player='aplay')

    spectrum = sound.make_spectrum()
    # # spectrum.low_pass(cutoff=600, factor=0.01)
    wave = spectrum.make_wave()
    #TODO: is this code really necessary - looks to me like we are constructing
    # a list with index, val where we already have an ordered list indexed with
    # those vals - what's the point??
    ans = []
    for i, amp in enumerate(spectrum.amps):
        tmp = []
        tmp.append(i)
        tmp.append(amp)
        ans.append(tmp)
    val = build_mag_output(ans)
    if val != 0:
        print(int(val))
        #cxn.write([int(val)])

def build_freq_output(data):
    '''
    determine what value to send over serial based on frequency of sound
    '''
    maxmag = 0
    for d in data:
        if d[1] > maxmag:
            maxmag = d[1]
            maxfreq = d[0]
    if maxfreq < 200:
        return 1
    elif maxfreq >= 200 and maxfreq < 400:
        return 2
    elif maxfreq >= 400 and maxfreq < 600:
        return 3
    elif maxfreq >= 600:
        return 4

def build_mag_output(data):
    '''
    determine what value to send over serial based on loudness of sound
    '''
    maxmag = 0
    for d in data:
        if d[1] > maxmag:
            if d[0] >1000 and d[0]<5000:
                maxmag = d[1]
                maxfreq = d[0]
    print(maxmag)
    if maxmag >= 20000:
        return 7
    elif maxmag >= 15000:
        return 6
    elif maxmag >= 10000:
        return 5
    elif maxmag >= 8000:
        return 4
    elif maxmag >= 5000:
        return 3
    elif maxmag >= 3000:
        return 2
    elif maxmag >= 1000:
        return 1
    return 0

if __name__ == '__main__':
    while True:
        record = threading.Thread(name='record', target=record_sound)
        process = threading.Thread(name='process', target=process_sound)
        try:
            record.start()
            process.start()
        except:
            print("unable to start thread")
        record.join()
        process.join()
    # wave.play('temp.wav')
    # spectrum.plot()
    # thinkplot.show()


    '''

    violin = thinkdsp.read_wave('input.wav')
	spectrum = violin.make_spectrum()
	for i, amp in enumerate(spectrum.amps):
	    print(i, amp)
	spectrum.plot()
    thinkplot.config(xlabel="Frequency", ylabel="Magnitude")
	thinkplot.show()
    '''
