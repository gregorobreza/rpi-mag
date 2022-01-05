import sys
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from random import randrange
from asyncio_mqtt import Client, MqttError
import websockets



async def bridge():
    while True:
        try:
            async with Client('192.168.1.185', username = 'gobreza', password = 'django4064') as client:
                async with websockets.connect('ws://192.168.1.185:8000/ws/some_urls/', ping_interval=None) as websocket:

                    async with client.filtered_messages("raspberry/data") as messages:
                            # subscribe is done afterwards so that we just start receiving messages 
                            # from this point on
                            await client.subscribe("raspberry/data")
                            async for message in messages:
                                #print(type(message.payload))
                                await websocket.send(message.payload)
                                #print(message.topic)
        except TypeError:
            print("format ni pravi")

asyncio.get_event_loop().run_until_complete(bridge())