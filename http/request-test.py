import requests

with open("test.txt", "rb") as a_file:

    file_dict = {"test.txt": a_file}

    response = requests.post("http://192.168.0.108:8001/measurement/upload/", files=file_dict)