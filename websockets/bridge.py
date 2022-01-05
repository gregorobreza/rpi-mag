import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from random import randrange
from asyncio_mqtt import Client, MqttError
import websockets



async def bridge():
    while True:
        try:
            async with Client("test.mosquitto.org",port=8080,transport="websockets") as client:
                async with websockets.connect('ws://192.168.1.233:8000/ws/some_urls/', ping_interval=None) as websocket:

                    async with client.filtered_messages("neki/neki") as messages:
                            # subscribe is done afterwards so that we just start receiving messages 
                            # from this point on
                            await client.subscribe("neki/neki")
                            async for message in messages:
                                await websocket.send(message.payload.decode())
                                print(message.topic)
                                print(message.payload.decode())
        except TypeError:
            print("format ni pravi")

asyncio.get_event_loop().run_until_complete(bridge())