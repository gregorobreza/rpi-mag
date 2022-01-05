import sys
import asyncio
import numpy as np
from contextlib import AsyncExitStack, asynccontextmanager
from random import randrange
from asyncio_mqtt import Client, MqttError





async def reciever():
    async with Client('192.168.1.185', username = 'gobreza', password = 'Django4064') as client:
        async with client.filtered_messages("raspberry/data") as messages:
            await client.subscribe("raspberry/data")
            async for message in messages:
                print(len(message.payload))
                numpydata = np.frombuffer(message.payload, dtype=np.int16)
                frame = np.stack((numpydata[::2], numpydata[1::2]), axis=0) 
                #print(message.payload)
                print(frame)
                print(len(numpydata))


asyncio.get_event_loop().run_until_complete(reciever())