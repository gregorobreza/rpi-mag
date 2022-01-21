from email import message
import paho.mqtt.client as mqtt
import os
import json
import numpy as np
from scipy.signal import csd


PATH = "../measurements"

last_state = {}
last_data = np.array([])

def transform_data(data):
    data = np.frombuffer(data, dtype=np.int16)
    frame = np.stack((data[::2], data[1::2]), axis=0)
    print(len(frame[1]))




# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("raspberry/data")
    client.subscribe("raspberry/control")
    client.subscribe("raspberry/status")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global last_state
    global last_data
    if msg.topic == "raspberry/control":
        message = msg.payload.decode()
        print(message)
        last_state = json.loads(message)
    elif msg.topic == "raspberry/status" and msg.payload.decode() == "finished":
        transform_data(last_data)
        last_data = np.array([])
    else:
        # print(msg.payload)
        # print(last_state)
        #numpydata = np.frombuffer(msg.payload, dtype=np.int16)
        last_data = np.append(last_data, msg.payload)
        if last_state["stream"] == "off":
            transform_data(last_data)
            last_data = np.array([])



client = mqtt.Client(client_id="calculate")
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(username = 'gobreza', password = 'Django4064')
# client.connect('192.168.0.108', 1883, 20)
client.connect('192.168.1.233', 1883, 20)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()