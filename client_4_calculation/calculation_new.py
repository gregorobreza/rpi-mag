import paho.mqtt.client as mqtt
import time
import logging
import numpy as np
import json
from scipy.signal import csd
import os
import errno
import shutil
from datetime import datetime

logger = logging.getLogger("IDS_LOGGER.refining")
logging.basicConfig(level=logging.INFO)

class calculation:


    def __init__(self):
        self.last_state = {}
        self.last_data = np.array([])
        self.files_path = "../measurements/"
        self.dir_name = "default"
        try:
            #self.BROKER_IP = '192.168.1.233'
            #self.BROKER_IP = '192.168.1.117'
            self.BROKER_IP = '192.168.0.108'
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
            #skaliranje iz int16
            input = (frame[1] * 2.1 * np.sqrt(2)) /((2**15)*0.1)
            output = (frame[0] * 2.1 * np.sqrt(2)) /((2**15)*0.47)
            self.get_frf(input, output)
            print(len(frame[1]))
            self.clean_data()
        else:
            self.clean_data()
            

    def get_frf(self, i, o, window="hann"):
        fs = self.last_state["rate"]
        duration = len(i) / fs
        print(duration)
        segments = self.last_state["segments"]
        # segments = 10
        
        freq, IO = csd(i, o, fs=fs, nperseg=int(fs)//segments, noverlap=int(fs)//(2*segments), scaling="spectrum",  window=window)
        freq, OI = csd(o, i, fs=fs, nperseg=int(fs)//segments, noverlap=int(fs)//(2*segments), scaling="spectrum",  window=window)
        freq, II = csd(i, i, fs=fs, nperseg=int(fs)//segments, noverlap=int(fs)//(2*segments), scaling="spectrum",  window=window)
        freq, OO = csd(o, o, fs=fs, nperseg=int(fs)//segments, noverlap=int(fs)//(2*segments), scaling="spectrum",  window=window)

        H1 = IO/II
        H2 = OO/OI
        coh = H1/H2

        now = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

        info = self.last_state
        info["duration"] = duration
        info["date"] = now
        self.dir_name = os.path.join(self.files_path, self.last_state["name"])

        if os.path.exists(self.dir_name):
            shutil.rmtree(self.dir_name)

        try:
            os.mkdir(self.dir_name)
        except IOError as e:
            if e.errno == 17:
                print("mapa obstaja")

        npinfo = np.array(list(info.items()))

        np.savez(self.dir_name +"/" + self.last_state["name"] + ".npz", **{"input": i, "output": o, "freq":freq, "H1":H1, "H2":H2, "coh":coh, "info":npinfo})
        np.savez("neki.npz", **{"input": i, "output": o, "freq":freq, "H1":H1, "H2":H2, "coh":coh, "info":npinfo})
        self.create_dict(freq, H1, H2, coh, info, i, o)


    def clean_data(self):
        self.last_data = np.array([])
        #print(len(self.last_data))

    def create_dict(self, freq, H1, H2, coh, info, i, o):
        """creates dictionary and json for view in JS"""

        #dicts = {"info": info, "H1":{}, "H2":{}, "angle":{}, "coh":{}}

        freq = freq.tolist()
        H1 = (20*np.log10(np.abs(H1))).tolist()
        H2 = (20*np.log10(np.abs(H2))).tolist()
        angle = np.angle(H1).tolist()
        coh = np.abs(coh).tolist()
        i = i.tolist()
        o = o.tolist()

        dicts = {"info": info, "freq":freq, "H1":H1, "H2":H2, "angle":angle, "coh":coh, "input":i, "output":o}

        # for i,j in enumerate(freq):
        #     dicts["H1"][j] = H1[i]
        #     dicts["H2"][j] = H2[i]
        #     dicts["angle"][j] = angle[i]
        #     dicts["coh"][j] = coh[i]
        #print(dicts)
        with open(self.dir_name + "/" + self.last_state["name"] + ".json", 'w') as outfile:
            json.dump(dicts, outfile)


if __name__ == "__main__":
    test = calculation()