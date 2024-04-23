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
        reload = config.getboolean('app', 'reload')
        return host, port, reload

@app.post("/select_detection/{detection_id}")
async def select_detection(detection_id: str):
        queue_dict[detection_id] = Queue(maxsize=1000)
        if not os.path.exists("select_detection"):
                return {"status": "error - detections folder missing"}
        if detection_id + ".mp4" not in os.listdir("select_detection"):
                return {"status": "error - detection not found"}
        
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
        
        host, port, do_reload = read_config()
                        
        # Create necessary directories
        os.makedirs("output_images", exist_ok=True)
        os.makedirs("example_vids", exist_ok=True)
        os.makedirs("select_detection", exist_ok=True)
        
        uvicorn.run("main:app", host=host, port=port, reload=do_reload)
