import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from random import randrange
from asyncio_mqtt import Client, MqttError

import json
import pyaudio

values = {'stream': 'off', 
            'rate': 96000, 
            'channels': 1, 
            'format': 0, 
            'chunk': 6}


FORMAT = pyaudio.paInt16
CHANNELS = values["channels"]
RATE = values["rate"]
CHUNK = int(RATE / 6)

audio = pyaudio.PyAudio()


        
async def advanced_example():
    # We 💛 context managers. Let's create a stack to help
    # us manage them.
    async with AsyncExitStack() as stack:
        # Keep track of the asyncio tasks that we create, so that
        # we can cancel them on exit
        tasks = set()
        stack.push_async_callback(cancel_tasks, tasks)
     

        # Connect to the MQTT broker
        client = Client('192.168.1.185', username = 'gobreza', password = 'Django4064')
        await stack.enter_async_context(client)

        # You can create any number of topic filters
        topic_filters = (
            "raspberry/control",
        )

        for topic_filter in topic_filters:
            # Log all messages that matches the filter
            manager = client.filtered_messages(topic_filter)
            messages = await stack.enter_async_context(manager)
            task = asyncio.create_task(receive(messages))
            tasks.add(task)


        # Messages that doesn't match a filter will get logged here


        # Subscribe to topic(s)
        # 🤔 Note that we subscribe *after* starting the message
        # loggers. Otherwise, we may miss retained messages.
        await client.subscribe("raspberry/#")

        # Publish a random value to each of these topics
        topics = (
            "raspberry/data",            
            
        )

        task = asyncio.create_task(send(client, topics))
        tasks.add(task)


        # Wait for everything to complete (or fail due to, e.g., network
        # errors)
        await asyncio.gather(*tasks)


async def receive(messages):
    async for message in messages:
        #print(message.topic)
        print(json.loads(message.payload))
        message = json.loads(message.payload)
        global values
        values = message
        #print(type(message))
        #return message
            


async def send(client, topics):
    while True :
        #print(values)
        if values["stream"] == "on":
            
            await stream_data(client, topics)
            #for topic in topics:
                
                #message = randrange(100)
                #print(f'[topic="{topic}"] Publishing message={message}')
                #await client.publish(topic, message, qos=1)
                #await asyncio.sleep(0.01)

        elif values["stream"] == "off":
            try:
                if stream.is_active():
                    stream.stop_stream()
                    stream.close()
            except UnboundLocalError:
                print("not yet defined")
            except NameError:
                print("defined somewere else")

            await asyncio.sleep(0.5)

        #else:
            #await asyncio.sleep(0.5)

async def stream_data(client, topics):
    for topic in topics:
        stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=1,
                        frames_per_buffer=CHUNK)
        await client.publish(topic, stream.read(CHUNK))



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