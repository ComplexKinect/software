import thinkdsp

violin = thinkdsp.read_wave('input.wav')
thinkdsp.play_wave(filename='input.wav',player='aplay')
