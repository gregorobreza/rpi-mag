import argparse
import tempfile
import queue
import sys

import sounddevice as sd
import soundfile as sf
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)


sd.default.device = 'snd_rpi_hifiberry_dacplusadcpro: HiFiBerry DAC+ADC PRO HiFi multicodec-0 (hw:1,0)'
#print(sd.query_devices())
samplerate = 192000
filename = tempfile.mktemp(prefix="test", suffix=".wav", dir="")
q = queue.Queue()



def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())

try:
    with sf.SoundFile(filename, mode='x', samplerate=samplerate, channels=2, subtype="PCM_24") as file:
        with sd.InputStream(samplerate=samplerate, channels=2, callback=callback):
            print('#' * 80)
            print('press Ctrl+C to stop the recording')
            print('#' * 80)
            while True:
                file.write(q.get())

except KeyboardInterrupt:
    print('\nRecording finished: ' + repr(filename))