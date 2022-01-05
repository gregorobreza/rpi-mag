import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from random import randrange
from asyncio_mqtt import Client, MqttError

import pyaudio
import json


FORMAT = pyaudio.paInt16
#FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 192000
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
        client = Client("test.mosquitto.org")
        await stack.enter_async_context(client)

        # You can create any number of topic filters
        topic_filters = (
            #"data/stream",
            #"data/comands",
            # 👉 Try to add more filters!
        )
        #for topic_filter in topic_filters:
            # Log all messages that matches the filter
         #   manager = client.filtered_messages(topic_filter)
            #print(manager)
         #   messages = await stack.enter_async_context(manager)
         #   template = f'[topic_filter="{topic_filter}"] {{}}'
          #  task = asyncio.create_task(log_messages(messages, template, topic_filter))
          #  tasks.add(task)


        stream_topic = "data/stream"
        
        messages = await stack.enter_async_context(client.filtered_messages("data/comands"))
        task = asyncio.create_task(record(client, stream_topic, messages))
        tasks.add(task)



        # Messages that doesn't match a filter will get logged here
        messages = await stack.enter_async_context(client.unfiltered_messages())
        task = asyncio.create_task(log_messages(messages, "[unfiltered] {}", None))
        tasks.add(task)

        # Subscribe to topic(s)
        # 🤔 Note that we subscribe *after* starting the message
        # loggers. Otherwise, we may miss retained messages.
        await client.subscribe("data/comands")
        #await client.subscribe("data/stream")

        # Publish a random value to each of these topics
        #topics = (
        #    "data/stream",
            # 👉 Try to add more topics!
        #)
        #task = asyncio.create_task(post_to_topics(client, topics))
        #tasks.add(task)

        # Wait for everything to complete (or fail due to, e.g., network
        # errors)
        await asyncio.gather(*tasks)

""" async def post_to_topics(client, topics):
    while True:
        for topic in topics:
            message = randrange(100)
            print(f'[topic="{topic}"] Publishing message={message}')
            await client.publish(topic, message, qos=0)
            await asyncio.sleep(1) """

async def log_messages(messages, template, topic):
    async for message in messages:
        #print(message.payload.decode())
        
        # 🤔 Note that we assume that the message paylod is an
        # UTF8-encoded string (hence the `bytes.decode` call).
        print(template.format(message.payload.decode()))

async def record(client, publish_topic, messages):
    async for message in messages:
        try:
            if message.payload.decode() == "On":
                    stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            input_device_index=1,
                            frames_per_buffer=CHUNK)
                    print("Stream opened")
                    await send_stream(client, publish_topic, stream.read(CHUNK))
            elif message.payload.decode() =="Off":
                stream.stop_stream()
                stream.close()
        except OSError as error:
            print(error)
            print("Naprava zasedena")

async def send_stream(client, topic, data):
    while True:
        await client.publish(topic, data, qos=0)


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