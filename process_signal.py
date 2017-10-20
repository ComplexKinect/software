import thinkdsp
import thinkplot

violin = thinkdsp.read_wave('input.wav')
spectrum = violin.make_spectrum()
for i, amp in enumerate(spectrum.amps):
    print(i, amp)
spectrum.plot()
thinkplot.show()
