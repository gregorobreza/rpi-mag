
import asyncio
import websockets
import json
import pyaudio
import wave


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
    async with websockets.connect('ws://192.168.1.233:8000/ws/some_urls/', ping_interval=None) as websocket:
        while True:
            data = stream.read(CHUNK)
            print(type(data))
            #a = bytearray(data)
            #print(a)
            await websocket.send(data)


asyncio.get_event_loop().run_until_complete(raspberry_client())