import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from random import randrange
from asyncio_mqtt import Client, MqttError

from distutils.util import strtobool




state = True

async def advanced_example():
    # We 💛 context managers. Let's create a stack to help
    # us manage them.
    async with AsyncExitStack() as stack:
        # Keep track of the asyncio tasks that we create, so that
        # we can cancel them on exit
        tasks = set()
        stack.push_async_callback(cancel_tasks, tasks)
     

        # Connect to the MQTT broker
        client = Client('192.168.1.233', username = 'gobreza', password = 'django4064')
        await stack.enter_async_context(client)

        # You can create any number of topic filters
        topic_filters = (
            "floors/+/humidity",
            "floors/rooftop/#",
            "data/bytes"
            # 👉 Try to add more filters!
        )

        for topic_filter in topic_filters:
            # Log all messages that matches the filter
            manager = client.filtered_messages(topic_filter)
            messages = await stack.enter_async_context(manager)
            template = f'[topic_filter="{topic_filter}"] {{}}'
            task = asyncio.create_task(log_messages(messages, template))
            tasks.add(task)

        control_messages = await stack.enter_async_context(client.filtered_messages("client/control"))
        task = asyncio.create_task(check_control_messages(control_messages))
        tasks.add(task)

        # Messages that doesn't match a filter will get logged here
        messages = await stack.enter_async_context(client.unfiltered_messages())
        task = asyncio.create_task(log_messages(messages, "[unfiltered] {}"))
        tasks.add(task)

        # Subscribe to topic(s)
        # 🤔 Note that we subscribe *after* starting the message
        # loggers. Otherwise, we may miss retained messages.
        await client.subscribe("floors/#")
        await client.subscribe("data/bytes")
        await client.subscribe("client/control")

        # Publish a random value to each of these topics
        topics = (
            "floors/basement/humidity",
            "floors/rooftop/humidity",
            "floors/rooftop/illuminance",
            # 👉 Try to add more topics!
        )

        status_topic = "senzor/status"
        task = asyncio.create_task(post_to_topics(client, topics, status_topic))
        tasks.add(task)


        # Wait for everything to complete (or fail due to, e.g., network
        # errors)
        await asyncio.gather(*tasks)

async def post_to_topics(client, topics, status_topic):

    while True:
        if state == True:
            print(state)
            for topic in topics:
                message = randrange(100)
                print(f'[topic="{topic}"] Publishing message={message}')
                await client.publish(topic, message, qos=0)
                await asyncio.sleep(1)
        else:
            status_message = "connected, standby"
            await client.publish(status_topic, status_message, qos=0)
            print("status:", status_message)
            await asyncio.sleep(3)
            



async def check_control_messages(messages):
    async for message in messages:
        # 🤔 Note that we assume that the message paylod is an
        # UTF8-encoded string (hence the `bytes.decode` call).
        info = message.payload.decode()
        global state 
        state = bool(strtobool(info))
        print("to je kontrolno sporocilo:", state)

async def log_messages(messages, template):
    async for message in messages:
        # 🤔 Note that we assume that the message paylod is an
        # UTF8-encoded string (hence the `bytes.decode` call).
        print(template.format(message.payload.decode()))

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