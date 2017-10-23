import thinkdsp
import thinkplot
import numpy as np

if __name__ == '__main__':
    cos_sig = thinkdsp.CosSignal(freq=440, amp=1.0, offset=0)
    sin_sig = thinkdsp.SinSignal(freq=880, amp=0.5, offset=0)
    mix = sin_sig + cos_sig

    wave = mix.make_wave(duration=0.5, start=0, framerate=11025)
    violin = thinkdsp.read_wave('output.wav')
    # wave.write(filename='output.wav')
    # thinkdsp.play_wave(filename='input.wav',player='aplay')

    spectrum = violin.make_spectrum()
    # # spectrum.low_pass(cutoff=600, factor=0.01)
    wave = spectrum.make_wave()
    # wave.play('temp.wav')
    spectrum.plot()
    thinkplot.config(xlabel="Frequency", ylabel="Magnitude")
    thinkplot.show()


    '''

    violin = thinkdsp.read_wave('input.wav')
	spectrum = violin.make_spectrum()
	for i, amp in enumerate(spectrum.amps):
	    print(i, amp)
	spectrum.plot()
	thinkplot.show()
    '''
