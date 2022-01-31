from email import message
import paho.mqtt.client as mqtt
import requests
import os
import json

import paho.mqtt.client as mqtt
import time
import logging
import numpy as np
import json
from scipy.signal import csd
import matplotlib.pyplot as plt
import os
import errno
import shutil

logger = logging.getLogger("IDS_LOGGER.refining")
logging.basicConfig(level=logging.INFO)




class list_measurements:


    def __init__(self):
        self.last_state = {}
        self.last_data = np.array([])
        self.files_path = "../measurements/"
        self.dir_name = "default"
        try:
            #self.BROKER_IP = '192.168.1.233'
            self.BROKER_IP = '192.168.1.117'
            #self.BROKER_IP = '192.168.0.108'
            self.client_id = "list_measurements"
            self.client = mqtt.Client(client_id = self.client_id)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.username_pw_set(username = 'gobreza', password = 'Django4064')
            self.client.connect(self.BROKER_IP, 1883, 20)
            self.topics = ["raspberry/check/measurements", "raspberry/check/measurements/download"]
            logging.info("Connected to {0}, starting MQTT loop".format(self.BROKER_IP))
            self.client.loop_forever()
        except Exception as e:
            print(e)


    def on_message(self,client, userdata,msg):
        """MQTT Callback function for handling received messages"""
        #print("message received!")
        message = msg.payload.decode()
        print(message)
        if msg.topic == "raspberry/check/measurements" and message == "list_files":
            self.list_files()

        elif msg.topic == "raspberry/check/measurements/download":
            print("POST")
            selected_folder = message
            print(selected_folder)
            self.post_files(selected_folder)
  
    def on_connect(self,client,userdata, flags, rc):
        print("connected")
        # self.client.subscribe("raspberry/data")
        for topic in self.topics:
            self.client.subscribe(topic)

    def list_files(self):
        folders = next(os.walk(self.files_path))[1]
        print(folders)
        msg = json.dumps(folders)
        self.client.publish("raspberry/measurements", payload=msg, qos=0, retain=False)


    def post_files(self, folder):
        json_file = os.path.join(self.files_path, folder) +"/" + folder + ".json"
        print(json_file)
        npz_file = os.path.join(self.files_path, folder) +"/" + folder + ".npz"
        print(npz_file)
        files = {'file1': open(json_file, 'rb'), 'file2': open(npz_file, 'rb')}
        response = requests.post("http://" + self.BROKER_IP +":8001/measurement/upload/" + folder +"/", files=files)


    

if __name__ == "__main__":
    test = list_measurements()