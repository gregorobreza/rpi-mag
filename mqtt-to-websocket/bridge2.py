import sys
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from random import randrange
from asyncio_mqtt import Client, MqttError
import websockets



IP = '192.168.1.117' #'192.168.1.233' '192.168.0.108'

async def bridge():
    
    while True:
        try:    
                async with Client(IP, username = 'gobreza', password = 'Django4064') as client:

                    async with websockets.connect('ws://' + IP + ':8001/ws/raspberry/data/', ping_interval=None) as websocket:

                        async with client.filtered_messages("raspberry/data") as messages:
                                # subscribe is done afterwards so that we just start receiving messages 
                                # from this point on
                                await client.subscribe("raspberry/data")
                                async for message in messages:

                                    await websocket.send(message.payload)

        except:
            print("neaktivnost")
            continue


asyncio.get_event_loop().run_until_complete(bridge())