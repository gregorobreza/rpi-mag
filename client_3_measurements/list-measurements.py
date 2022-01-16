from email import message
import paho.mqtt.client as mqtt
import requests
import os
import json


PATH = "../measurements"

def list_files(path):
    files = os.listdir(path)
    msg = json.dumps(files)
    client.publish("raspberry/measurements", payload=msg, qos=0, retain=False)


def post_file(path, file):
    file_path = path + "/" + file
    with open(file_path, "rb") as a_file:
        file_dict = {file: a_file}
        response = requests.post("http://192.168.0.108:8001/measurement/upload/" + file +"/", files=file_dict)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("raspberry/check/measurements")
    client.subscribe("raspberry/check/measurements/download")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(msg.topic+" "+ msg.payload.decode())
    if msg.topic == "raspberry/check/measurements" and message == "list_files":
        list_files(PATH)
    elif msg.topic == "raspberry/check/measurements/download":
        print("POST")
        selected_file = message
        post_file(PATH, selected_file)


client = mqtt.Client(client_id="list measurements")
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(username = 'gobreza', password = 'Django4064')
client.connect('192.168.0.108', 1883, 20)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()