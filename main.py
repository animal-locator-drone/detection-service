import requests
import time
import random
from uuid import uuid4
from collections import deque
from multiprocessing import Process, Queue

from dog_detector import *


def post_detection_random(data):
    response = requests.post('http://localhost:3000/new_detection', json=data)
    print(response)


def post_detections_from_queue(queue):
#     time.sleep(5)
    while True:
        if not queue.empty():
            print("posting detection")
            data = queue.get()
            post_detection_random(data)


def main(queue):
#     time.sleep(5)
    for confidences, boxes, cropped_images in generate_predictions():
        data = {
            "id": str(uuid4()),
            "time": time.time(),
            "images": cropped_images,
            "location": [random.randint(0, 100), random.randint(0, 100)]
        }
        print("appending to queue")
        queue.put(data)


if __name__ == '__main__':
    detections_queue = Queue(maxsize=100)

    main_process = Process(target=main, args=(detections_queue,))
    main_process.start()
    print("main process started")

    post_process = Process(target=post_detections_from_queue, args=(detections_queue,))
    post_process.start()
    print("post process started")

    main_process.join()
    post_process.join()
