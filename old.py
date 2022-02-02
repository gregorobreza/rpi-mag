    def check_value(self, buffer):
        data = np.frombuffer(buffer, dtype=np.int16)
        frame = np.stack((data[::2], data[1::2]), axis=0)
        if np.max(frame[0]) > 150 or np.min(frame[0]) < -150:
            self.last_data = np.append(self.last_data, data)
        elif self.last_data.size > self.last_data["rate"] and (np.max(frame[0]) < 250 or np.min(frame[0]) > - 250):
            msg = {"stream":"off", "save":"no"}
            msg = json.dumps(msg)
            self.client.publish("raspberry/control", payload=msg, qos=0, retain=False)
            self.transform_data(self.last_data)
        elif self.last_data.size < self.last_data["rate"] and self.last_data.size !=0:
            self.last_data = np.append(self.last_data, data)