import pyaudio
import wave
import time
import thinkdsp
import thinkplot
import numpy as np


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

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")
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
    cos_sig = thinkdsp.CosSignal(freq=440, amp=1.0, offset=0)
    sin_sig = thinkdsp.SinSignal(freq=880, amp=0.5, offset=0)
    mix = sin_sig + cos_sig

    wave = mix.make_wave(duration=0.5, start=0, framerate=11025)
    violin = thinkdsp.read_wave('tester.wav')
    # wave.write(filename='output.wav')
    # thinkdsp.play_wave(filename='input.wav',player='aplay')

    spectrum = violin.make_spectrum()
    # # spectrum.low_pass(cutoff=600, factor=0.01)
    wave = spectrum.make_wave()
    ans = []
    for i, amp in enumerate(spectrum.amps):
        tmp = []
        tmp.append(i)
        tmp.append(amp)
        ans.append(tmp)
    print(ans[1])



if __name__ == '__main__':
    while True:
        record_sound()
        process_sound()
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
