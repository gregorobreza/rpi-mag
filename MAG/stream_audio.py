import sounddevice as sd
import soundfile as sf

import json
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)


sd.default.device = 'snd_rpi_hifiberry_dacplusadcpro: HiFiBerry DAC+ADC PRO HiFi multicodec-0 (hw:1,0)'
#print(sd.query_devices())
fs = 192000
duration = 5

import sounddevice as sd
duration = 5  # seconds

def callback(indata, frames , time, status):
    if status:
        print(status)
    print(time.inputBufferAdcTime)
    print(time.currentTime)
    buffer = indata
    print(buffer[1])
    

with sd.InputStream(samplerate=fs, blocksize=48000, channels=1, dtype='int24', callback=callback):
    sd.sleep(int(duration * 1000))