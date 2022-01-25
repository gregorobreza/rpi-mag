import sys
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from random import randrange
from asyncio_mqtt import Client, MqttError

import json
import pyaudio

from getmac import get_mac_address
import socket

import numpy as np
import json


audio = pyaudio.PyAudio()
card = audio.get_device_info_by_index(1)['name'].split(":")[0]
mac = get_mac_address()
host_name = socket.gethostname()


#default values
values = {'mode': "stream",
            'stream':'off',
            'duration':2.5,
            'rate': 192000, 
            'channels': 2, 
            'format': pyaudio.paInt16, 
            'chunk': 360000}



#FORMAT = pyaudio.paInt16
#CHANNELS = values["channels"]
#RATE = values["rate"]
#CHUNK = int(RATE / 6)


def define_values(**kwargs):
    format = {
        "int8": pyaudio.paInt8,
        "int16": pyaudio.paInt16,
        "int24": pyaudio.paInt24,
        "int32": pyaudio.paInt32,
        "float32": pyaudio.paFloat32
    }
    #print(kwargs.items())
    if "format" in kwargs.keys():
        kwargs["format"] = format[kwargs["format"]]
    global values
    values = {key: kwargs.get(key, values[key]) for key in values}
    #values = kwargs
        
async def advanced_example():

    async with AsyncExitStack() as stack:
        # Keep track of the asyncio tasks that we create, so that
        # we can cancel them on exit
        tasks = set()
        stack.push_async_callback(cancel_tasks, tasks)
     

        # Connect to the MQTT broker
        client = Client('192.168.1.233', username = 'gobreza', password = 'Django4064', client_id=host_name)
        # client = Client('192.168.0.108', username = 'gobreza', password = 'Django4064', client_id=host_name)
        await stack.enter_async_context(client)

        # You can create any number of topic filters
        topic_filters = (
            "raspberry/control",
            "raspberry/status",
            "raspberry/check"
        )

        for topic_filter in topic_filters:
            
            manager = client.filtered_messages(topic_filter)
            messages = await stack.enter_async_context(manager)
            task = asyncio.create_task(receive(messages, client))
            tasks.add(task)


        # Subscribe to topic(s)
        # 🤔 Note that we subscribe *after* starting the message
        # loggers. Otherwise, we may miss retained messages.
        await client.subscribe("raspberry/#")


        task = asyncio.create_task(send(client))
        tasks.add(task)


        # Wait for everything to complete (or fail due to, e.g., network
        # errors)
        await asyncio.gather(*tasks)


async def receive(messages, client):
    async for message in messages:
        #print(message.payload.decode())
        if message.topic == "raspberry/check" and message.payload.decode() == "status":
            message = {"host name": host_name, "MAC":mac,"status":"connected", "card":card}
            await client.publish("raspberry/status", payload=json.dumps(message))
        #print(message.topic)
        elif message.topic == "raspberry/control":
            print(json.loads(message.payload))
            message = json.loads(message.payload)
            #global values
            #values = message
            define_values(**message)


async def send(client):
    stream = audio.open(format=values["format"], 
                        channels=int(values["channels"]),
                        rate=values["rate"], input=True, 
                        input_device_index=1, 
                        frames_per_buffer=values["chunk"])
    
    while True :
        if values["mode"] == "stream":
            if values["stream"] == "on":
                
                try:
                    stream.start_stream()
                except OSError:
                    stream.__init__(audio, rate=values["rate"], channels=values["channels"], format=values["format"], 
                    input=True, input_device_index=1, frames_per_buffer=values["chunk"])
                    #print(values)
                #print(sys.getsizeof(stream.read(CHUNK)))
                #print(len(stream.read(values["chunk"])))
                try:
                    # numpydata = np.frombuffer(stream.read(values["chunk"]), dtype=np.int16)
                    # list = numpydata.tolist()
                    # json_str = json.dumps(list)
                    # await client.publish("raspberry/data", json_str, qos=0)
                    await client.publish("raspberry/data", stream.read(values["chunk"], exception_on_overflow=False), qos=0)
                except OSError:
                    print("Input overflow, please choose bigger buffer")
                    await client.publish("raspberry/data", "Input overflow")
                    await asyncio.sleep(0.5)
                    define_values(**{"stream":"off"})
                    stream.__init__(audio, rate=values["rate"], channels=int(values["channels"]), format=values["format"], input=True, input_device_index=1, frames_per_buffer=values["chunk"])

            elif values["stream"] == "off":
                try:
                    if stream.is_active():
                        #print("active")
                        stream.stop_stream()
                        stream.close()
                except OSError:
                    pass
                    #print("stream not active")
                # message = {"host name": host_name, "MAC":mac,"status":"connected", "stream":"not active"}
                # await client.publish("raspberry/status", payload=json.dumps(message))
                await asyncio.sleep(0.1)

        elif values["mode"] == "duration" and values["stream"] == "on":

            try:
                stream.start_stream()
            except OSError:
                stream.__init__(audio, rate=values["rate"], channels=int(values["channels"]), format=values["format"], input=True, input_device_index=1, frames_per_buffer=values["chunk"])
                    #print(values)
                #print(sys.getsizeof(stream.read(CHUNK)))
                #print(len(stream.read(values["chunk"])))
            try:
                for _ in range(0, int(values["rate"]/values["chunk"] * values["duration"])):
                    await client.publish("raspberry/data", stream.read(values["chunk"], exception_on_overflow=False))
                await client.publish("raspberry/status", "finished")
                print(f'The time {values["duration"]}s is up')
                define_values(**{"mode":"stream", "stream":"off"})
                stream.stop_stream()
                stream.close()

            except OSError:
                print("Input overflow, please choose bigger buffer")
                await client.publish("raspberry/status", "Input overflow")
                await asyncio.sleep(0.5)
                define_values(**{"mode":"stream", "stream":"off"})
                stream.__init__(audio, rate=values["rate"], channels=int(values["channels"]), format=values["format"], input=True, input_device_index=1, frames_per_buffer=values["chunk"])




async def cancel_tasks(tasks):
    for task in tasks:
        if task.done():
            continue
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

async def main():
    # Run the advanced_example indefinitely. Reconnect automatically
    # if the connection is lost.
    reconnect_interval = 3  # [seconds]
    while True:
        try:
            await advanced_example()
        except MqttError as error:
            print(f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
        finally:
            await asyncio.sleep(reconnect_interval)


asyncio.run(main())