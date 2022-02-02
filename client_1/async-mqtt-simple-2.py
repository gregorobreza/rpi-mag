# Uvoz potrebnih knjizic
import sys
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from random import randrange
from asyncio_mqtt import Client, MqttError
import json
import pyaudio
from getmac import get_mac_address
import socket
import json

# kreiranje instance razreda PyAudio za upravljanje z nadgradnjo
audio = pyaudio.PyAudio()
# pridobitev informacij o napravi
card = audio.get_device_info_by_index(1)['name'].split(":")[0]
mac = get_mac_address()
host_name = socket.gethostname()
# definicija IP ali DNS naslova streznika
IP = '192.168.1.117'  #'192.168.0.108'  '192.168.1.233'
# privzeto stanje
values = {'mode': "stream",
            'stream':'off',
            'duration':2.5,
            'rate': 192000, 
            'channels': 2, 
            'format': pyaudio.paInt16, 
            'chunk': 8000}

def define_values(**kwargs):
    """funkcija spremeni globalno spremenljivko stanja"""
    format = {
        "int16": pyaudio.paInt16,
     }
    if "format" in kwargs.keys():
        kwargs["format"] = format[kwargs["format"]]
    global values
    values = {key: kwargs.get(key, values[key]) for key in values}
        

async def client_1():
    """vspostavi povezavo z MQTT in
    definira opravila"""

    async with AsyncExitStack() as stack:
        tasks = set()
        stack.push_async_callback(cancel_tasks, tasks)
        # Povezava z MQTT posrednikom 
        client = Client(IP, username = 'gobreza', password = 'Django4064', client_id=host_name)
        await stack.enter_async_context(client)
        # Izbira tem
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

        await client.subscribe("raspberry/#")

        task = asyncio.create_task(send(client))
        tasks.add(task)
        await asyncio.gather(*tasks)


async def receive(messages, client):
    """Funkcija, ki skrbi za prejeta sporocila in
    ustrezno spremembo stanja"""
    async for message in messages:
        if message.topic == "raspberry/check" and message.payload.decode() == "status":
            message = {"host name": host_name, "MAC":mac,"status":"connected", "card":card}
            await client.publish("raspberry/status", payload=json.dumps(message))
        elif message.topic == "raspberry/control":
            print(json.loads(message.payload))
            message = json.loads(message.payload)
            define_values(**message)

async def send(client):
    """Funkcija, ki skrbi za posiljanje toka podatkov"""
    stream = audio.open(format=values["format"], 
                        channels=int(values["channels"]),
                        rate=values["rate"], input=True, 
                        input_device_index=1, 
                        frames_per_buffer=values["chunk"])
    
    while True :
        # Preverjanj stanja in posiljanje paketov glede na
        # trenutno stanje
        if values["mode"] == "stream":
            # neomejen nacin zajema
            if values["stream"] == "on":
                try:
                    stream.start_stream()
                except OSError:
                    stream.__init__(audio, rate=values["rate"], channels=values["channels"], format=values["format"], 
                    input=True, input_device_index=1, frames_per_buffer=values["chunk"])
                try:
 
                    await client.publish("raspberry/data", stream.read(values["chunk"], exception_on_overflow=False), qos=0)
                except OSError:
                    print("Prosim zberite vecji buffer.")
                    await client.publish("raspberry/data", "Input overflow")
                    await asyncio.sleep(0.5)
                    define_values(**{"stream":"off"})
                    stream.__init__(audio, rate=values["rate"], channels=int(values["channels"]), format=values["format"], input=True, input_device_index=1, frames_per_buffer=values["chunk"])

            elif values["stream"] == "off":
                try:
                    if stream.is_active():
                        stream.stop_stream()
                        stream.close()
                except OSError:
                    pass
                    #print("tok trenutno ni aktiven")
                await asyncio.sleep(0.1)

        elif values["mode"] == "duration" and values["stream"] == "on":
            # omejen nacin zajema
            try:
                stream.start_stream()
            except OSError:
                stream.__init__(audio, rate=values["rate"], channels=int(values["channels"]), format=values["format"], input=True, input_device_index=1, frames_per_buffer=values["chunk"])

            try:
                for _ in range(0, int(values["rate"]/values["chunk"] * values["duration"])):
                    await client.publish("raspberry/data", stream.read(values["chunk"], exception_on_overflow=False))
                await client.publish("raspberry/status", "finished")
                print(f'The time {values["duration"]}s is up')
                define_values(**{"mode":"stream", "stream":"off"})
                stream.stop_stream()
                stream.close()

            except OSError:
                print("Prosimo izberite vecji buffer")
                await client.publish("raspberry/status", "Input overflow")
                await asyncio.sleep(0.5)
                define_values(**{"mode":"stream", "stream":"off"})
                stream.__init__(audio, rate=values["rate"], channels=int(values["channels"]), format=values["format"], input=True, input_device_index=1, frames_per_buffer=values["chunk"])


async def cancel_tasks(tasks):
    """Ko se taski zakljucijo ali ce mi ustavimo
    program jih zapremo"""
    for task in tasks:
        if task.done():
            continue
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

async def main():
    """Izvajanje programa neskoncno, ce
     MQTT posrednika ni, se poskusimo ponovno povezati"""
    reconnect_interval = 3  # [seconds]
    while True:
        try:
            await client_1()
        except MqttError as error:
            print(f'Error "{error}". Ponovna povezava cez {reconnect_interval} seconds.')
        finally:
            await asyncio.sleep(reconnect_interval)

asyncio.run(main())