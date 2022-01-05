import asyncio
import websockets
import json
import pyaudio
import queue
from asyncio_mqtt import Client, MqttError
import numpy as np




import sounddevice as sd



sd.default.device = 1

samplerate = 192000

stream = sd.InputStream(samplerate=192000, channels=1, dtype='int32')
stream.start()
print(stream.read(1024))
#sd.sleep(5000)



#async def raspberry_client():
#    async with Client('192.168.1.233', username = 'gobreza', password = 'django4064') as client:
#        while True:
            #data = stream.read(CHUNK)
            #print(type(data))
            #a = bytearray(data)
            #print(a)
            #await client.publish("data/stream", a, qos=0, retain=False)


#asyncio.get_event_loop().run_until_complete(raspberry_client())