import paho.mqtt.client as mqtt
import time
import logging
import numpy as np
import json
from scipy.signal import csd
import matplotlib.pyplot as plt

logger = logging.getLogger("IDS_LOGGER.refining")
logging.basicConfig(level=logging.INFO)

class calculation:


    def __init__(self):
        self.last_state = {}
        self.last_data = np.array([])
        self.files_path = "../measurements/"
        try:
            self.BROKER_IP = '192.168.1.233'
            #self.BROKER_IP = '192.168.0.108'
            self.client_id = "calculate"
            self.client = mqtt.Client(client_id = self.client_id)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.username_pw_set(username = 'gobreza', password = 'Django4064')
            self.client.connect(self.BROKER_IP, 1883, 20)
            self.topics = ["raspberry/data", "raspberry/control", "raspberry/status"]
            logging.info("Connected to {0}, starting MQTT loop".format(self.BROKER_IP))
            self.client.loop_forever()
        except Exception as e:
            print(e)


    def on_message(self,client, userdata,msg):
        """MQTT Callback function for handling received messages"""
        #print("message received!")
        #print(msg.payload.decode())
        if msg.topic == "raspberry/control":
            message = msg.payload.decode()
            self.last_state = json.loads(message)
            # print(self.last_state)
        elif msg.topic == "raspberry/status" and msg.payload.decode() == "finished":
            self.transform_data(self.last_data)
            # self.clean_data()
            # print(len(self.last_data))
        elif msg.topic == "raspberry/data":
            if self.last_state["save"] == "yes":
                self.last_data = np.append(self.last_data, msg.payload)
            if self.last_state["stream"] == "off":
                self.transform_data(self.last_data)
                # self.clean_data()
                # print(len(self.last_data))
  
    def on_connect(self,client,userdata, flags, rc):
        print("connected")
        # self.client.subscribe("raspberry/data")
        for topic in self.topics:
            self.client.subscribe(topic)

    def transform_data(self, data):
        if data.size != 0:
            data = np.frombuffer(data, dtype=np.int16)
            frame = np.stack((data[::2], data[1::2]), axis=0)
            input = frame[0]
            output = frame[1]
            self.get_frf(input, output)
            print(len(frame[1]))
            self.clean_data()
        else:
            self.clean_data()
            

    def get_frf(self, i, o, window="hann"):
        fs = self.last_state["rate"]
        freq, IO = csd(i, o, fs=fs, scaling="spectrum", nperseg=1024, window=window)
        freq, OI = csd(o, i, fs=fs, scaling="spectrum", nperseg=1024, window=window)
        freq, II = csd(i, i, fs=fs, scaling="spectrum", nperseg=1024, window=window)
        freq, OO = csd(o, o, fs=fs, scaling="spectrum", nperseg=1024, window=window)

        H1 = IO/II
        H2 = OO/OI
        coh = H1/H2
        # print(H1)
        # print(H2)
        print(freq)
        np.savez(self.files_path + self.last_state["name"] + ".npz", **{"input": i, "output": o, "freq":freq, "H1":H1, "H2":H2, "coh":coh})
        np.savez("neki.npz", **{"input": i, "output": o, "freq":freq, "H1":H1, "H2":H2, "coh":coh})
        self.create_dict(freq, H1, H2, coh)


    def clean_data(self):
        self.last_data = np.array([])
        #print(len(self.last_data))

    def create_dict(self, freq, H1, H2, coh):
        """creates dictionary and json for view in JS"""
        dicts = {"H1":{}, "H2":{}, "angle":{}, "coh":{}}
        freq = freq.tolist()
        H1 = 20*np.log10(np.abs(H1)).tolist()
        H2 = 20*np.log10(np.abs(H2)).tolist()
        angle = np.angle(H1)
        coh = np.abs(coh).tolist()

        for i,j in enumerate(freq):
            dicts["H1"][j] = H1[i]
            dicts["H2"][j] = H2[i]
            dicts["angle"][j] = angle[i]
            dicts["coh"][j] = coh[i]

        with open('json_data.json', 'w') as outfile:
            json.dump(dicts, outfile)



test = calculation()