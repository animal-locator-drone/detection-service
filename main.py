import os
import requests
import time
import random
from uuid import uuid4
from multiprocessing import Process, Queue

from fastapi import FastAPI
from pydantic import BaseModel
from configparser import ConfigParser
import uvicorn

app = FastAPI()

from dog_detector import *

def read_config():
    # Read configuration from config.ini
    config = ConfigParser()
    config.read('config.ini')
    # Get configuration values
    host = config.get('app', 'host')
    port = config.getint('app', 'port')
    reload = config.getboolean('app', 'reload')
    return host, port, reload

def post_detection(data):
        response = requests.post('http://localhost:3000/new_detection',
                                 json=data)
        
        # Upload image to server
        files = {'image': open(data["images"][0], 'rb')}
        image_data = {
                "name": data["id"]
        }
        response = requests.post('http://localhost:3000/upload_image',
                                 files=files)
        # print(response)


def post_detections_from_queue(queue):
        while True:
                if not queue.empty():
                        # print("posting detection")
                        data = queue.get()
                        post_detection(data)

def process_cropped_images(cropped_images):
        for cropped_image in cropped_images:
                data = {
                    "id":
                    str(uuid4()),
                    "time":
                    time.time(),
                    "images": [f"output_images/{cropped_image}"],
                    "location":
                    [random.randint(0, 100),
                     random.randint(0, 100)]
                }
                
                yield data

def main(queue):
        model_name = "yolov8n.pt"
        vid_src = './example_vids/dogs_small.mp4'
        for cropped_images in generate_prediction_images(model_name, vid_src):
                if len(cropped_images) == 0:
                        continue
                
                for data in process_cropped_images(cropped_images):
                        queue.put(data)


if __name__ == '__main__':
        
        host, port, reload = read_config()
                        
        # Create necessary directories
        os.makedirs("output_images", exist_ok=True)
        os.makedirs("example_vids", exist_ok=True)
        
        detections_queue = Queue(maxsize=1000)

        main_process = Process(target=main, args=(detections_queue, ))
        main_process.start()
        print("main process started")

        post_process = Process(target=post_detections_from_queue,
                               args=(detections_queue, ))
        post_process.start()
        print("post process started")

        
        uvicorn.run(app, host=host, port=port, reload=reload)
        main_process.join()
        post_process.join()
