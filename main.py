import aiohttp
import asyncio
import time
import random
from uuid import uuid4
from collections import deque

detections_queue = deque(maxlen=100)

async def post_detection_random(session, data):
        async with session.post('http://localhost:3000/new_detection', json=data) as response:
                print(await response.text())
                
async def post_detections_from_queue():
        session = aiohttp.ClientSession()
        while True:
                if len(detections_queue) > 0:
                        data = detections_queue.popleft()
                        await post_detection_random(session, data)
                print("Next post in 2 seconds")
                await asyncio.sleep(2)
       

async def main():
        while True:
                detection_roll = random.randint(0, 100)
                if detection_roll > 50:
                        # Somewhere we will need to also asyncronously save the images to disk
                        detections_queue.append({
                                "id": str(uuid4()),
                                "time": time.time(),
                                "images": ["image1.jpg", "image2.jpg"],
                                "location": [random.randint(0, 100), random.randint(0, 100)]
                        })
                print("Next detection in 1 second")
                await asyncio.sleep(1)

# Run the main function in an event loop
loop = asyncio.get_event_loop()
loop.create_task(main())
loop.create_task(post_detections_from_queue())
loop.run_forever()

                        