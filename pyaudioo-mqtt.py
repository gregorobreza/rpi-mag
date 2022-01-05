
import asyncio
import websockets
import json
import pyaudio
import wave
from asyncio_mqtt import Client, MqttError


FORMAT = pyaudio.paInt16
#FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 192000
CHUNK = int(RATE / 6)

audio = pyaudio.PyAudio()

stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=1,
                    frames_per_buffer=CHUNK)


async def raspberry_client():
    async with Client('192.168.1.233', username = 'gobreza', password = 'django4064') as client:
        while True:
            data = stream.read(CHUNK)
            #print(type(data))
            a = bytearray(data)
            #print(a)
            await client.publish("data/stream", a, qos=0, retain=False)


asyncio.get_event_loop().run_until_complete(raspberry_client())