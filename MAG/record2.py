

import sounddevice as sd
import soundfile as sf

import json
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)
#import matplotlib as plt

sd.default.device = 'snd_rpi_hifiberry_dacplusadcpro: HiFiBerry DAC+ADC PRO HiFi multicodec-0 (hw:1,0)'
#print(sd.query_devices())
fs = 192000
duration = 5

myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)

sd.wait()
#json_str = json.dumps(myrecording.tolist())
print(len(myrecording))



