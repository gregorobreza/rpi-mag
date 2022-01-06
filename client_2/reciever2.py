import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from random import randrange
from asyncio_mqtt import Client, MqttError, client
import numpy as np



CONTROL = {}
test_array = np.array([])

async def advanced_example():
    # We 💛 context managers. Let's create a stack to help
    # us manage them.
    async with AsyncExitStack() as stack:
        # Keep track of the asyncio tasks that we create, so that
        # we can cancel them on exit
        tasks = set()
        stack.push_async_callback(cancel_tasks, tasks)

        # Connect to the MQTT broker
        client = Clientclient = Client('192.168.1.185', username = 'gobreza', password = 'Django4064', client_id="raspberrypi-calculation")
        await stack.enter_async_context(client)

        # You can create any number of topic filters
        topic_filters = (
            "raspberry/control",
            "raspberry/data",
            "raspberry/status"
            # 👉 Try to add more filters!
        )
        for topic_filter in topic_filters:
            # Log all messages that matches the filter
            manager = client.filtered_messages(topic_filter)
            messages = await stack.enter_async_context(manager)
            #template = f'[topic_filter="{topic_filter}"] {{}}'
            task = asyncio.create_task(log_messages(messages, client))
            tasks.add(task)


        # Subscribe to topic(s)
        # 🤔 Note that we subscribe *after* starting the message
        # loggers. Otherwise, we may miss retained messages.
        await client.subscribe("raspberry/#")

        # Wait for everything to complete (or fail due to, e.g., network
        # errors)
        await asyncio.gather(*tasks)


async def log_messages(messages, client):
    global test_array
    global CONTROL
    count = 0
    async for message in messages:
        if message.topic == "raspberry/status":
            text = message.payload.decode()
            print(text)
        elif message.topic == "raspberry/data":

            numpydata = np.frombuffer(message.payload, dtype=np.int16)
            #test_array = np.append(test_array, numpydata)
            count += len(numpydata)
            print(numpydata)
            print(count)
            await client.publish("raspberry/calculation", numpydata.tobytes())
        elif message.topic == "raspberry/control":
            CONTROL = message.payload.decode()
            print(CONTROL)
        # 🤔 Note that we assume that the message paylod is an
        # UTF8-encoded string (hence the `bytes.decode` call).
        #print(message.topic)
        #print(template.format(message.payload.decode()))
        

async def cancel_tasks(tasks):
    for task in tasks:
        if task.done():
            continue
        try:
            task.cancel()
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