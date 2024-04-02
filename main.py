import requests
import time
import random
from uuid import uuid4
from collections import deque
from multiprocessing import Process, Queue

from dog_detector import *


def post_detection_random(data):
        response = requests.post('http://localhost:3000/new_detection',
                                 json=data)
        # print(response)


def post_detections_from_queue(queue):
        while True:
                if not queue.empty():
                        # print("posting detection")
                        data = queue.get()
                        post_detection_random(data)

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
        for cropped_images in generate_prediction_images(
            'yolov8n.pt', './example_vids/dogs_small.mp4'):
                if len(cropped_images) == 0:
                        continue
                
                for data in process_cropped_images(cropped_images):
                        queue.put(data)


if __name__ == '__main__':
        detections_queue = Queue(maxsize=1000)

        main_process = Process(target=main, args=(detections_queue, ))
        main_process.start()
        # print("main process started")

        post_process = Process(target=post_detections_from_queue,
                               args=(detections_queue, ))
        post_process.start()
        # print("post process started")

        main_process.join()
        post_process.join()
