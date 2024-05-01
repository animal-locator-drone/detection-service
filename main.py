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

# Dictionaries to keep track of running processes and their respective queues
main_process_dict = {}
post_process_dict = {}
queue_dict = {}

app = FastAPI()

from dog_detector import *

def read_config():
        # Read configuration from config.ini
        config = ConfigParser()
        config.read('config.ini')
        # Get configuration values
        host = config.get('app', 'host')
        port = config.getint('app', 'port')
        do_reload = config.getboolean('app', 'reload')
        app_port = config.getint('app', 'app_port')
        app_host = config.get('app', 'app_host')
        return host, port, do_reload, app_port, app_host

@app.post("/select_detection/{detection_id}")
async def select_detection(detection_id: str):
        if not os.path.exists("select_detection"):
                return {"status": "error - detections folder missing"}
        if detection_id + ".mp4" not in os.listdir("select_detection"):
                return {"status": "error - detection not found"}
        if main_process_dict.get(detection_id):
                return {"status": "success"}
        if post_process_dict.get(detection_id):
                return {"status": "success"}
        
        queue_dict[detection_id] = Queue(maxsize=1000)
        main_process_dict[detection_id] = Process(
                target=main,
                args=(queue_dict[detection_id], detection_id)
        )
        main_process_dict[detection_id].start()
        print("main process started for", detection_id)

        
        post_process_dict[detection_id] = Process(
                target=post_detections_from_queue,
                args=(queue_dict[detection_id], )
        )
        post_process_dict[detection_id].start()
        print("post process started for", detection_id)
        
        return {"status": "success"}
       

def post_detection(data):
        app_port, app_host = read_config()[3:]
        print("app_host", app_host)
        print("app_port", app_port)
        response = requests.post(f'http://{app_host}:{app_port}/new_detection',
                                 json=data)
        
        # Upload image to server
        files = {'image': open(data["images"][0], 'rb')}
        image_data = {
                "name": data["id"]
        }
        response = requests.post(f'http://{app_host}:{app_port}/upload_image',
                                 files=files)


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

def main(queue, detection_id):
        model_name = "yolov8n.pt"
        vid_src = './select_detection/' + detection_id + ".mp4"
        print("Starting main process")
        for cropped_images in generate_prediction_images(model_name, vid_src):
                # print("Processing cropped images")
                if len(cropped_images) == 0:
                        # print("No detections")
                        continue
                
                for data in process_cropped_images(cropped_images):
                        # print("Putting data in queue")
                        queue.put(data)


if __name__ == '__main__':
        
        host, port, do_reload, app_host, app_port = read_config()
                        
        # Create necessary directories
        os.makedirs("output_images", exist_ok=True)
        os.makedirs("example_vids", exist_ok=True)
        os.makedirs("select_detection", exist_ok=True)
        
        uvicorn.run("main:app", host=host, port=port, reload=do_reload)
        
        for detection_id in main_process_dict:
                main_process_dict[detection_id].join()
                post_process_dict[detection_id].join()
        
