from torch import tensor
from ultralytics import YOLO
import cv2
from uuid import uuid4

# model = YOLO("yolov8n.pt")  # initialize model
# results = model(source='./dogs.mp4', show=True, conf=0.4, stream=True)  # detect video stream

# for result in results:
#         boxes = result.boxes
#         confidences = list(zip(boxes.cls, boxes.conf))
#         names = result.names
        
#         # Print out the class confidence and bounding box coordinates
#         class_confidence = result.probs
        
#         if len(boxes) > 0:
#                 print("Class confidence: ", confidences)
        
#                 print("Boxes: ", boxes)
#                 print("Names: ", names)
#                 print("---------------------------------------------------")

def construct_cropped_images(boxes, original_image):
        images = []
        for box in boxes:
                # print(box.cls)
                if box.cls != tensor([16.]):
                        continue
                xyxy_format = box.xyxy[0]
                # print(xyxy_format)
                x1, y1, x2, y2 = xyxy_format[0], xyxy_format[1], xyxy_format[2], xyxy_format[3]
                cropped_image = original_image[int(y1):int(y2), int(x1):int(x2)]
                images.append(cropped_image)
        # save images
        
        image_names = [f"cropped_image_{i}_{str(uuid4())}.jpg" for i in range(len(images))]
        
        for i, image in enumerate(images):
                cv2.imwrite("./output_images/"+image_names[i], image)
                
        return image_names

def generate_predictions():
        model = YOLO("yolov8n.pt")  # initialize model
        results = model(source='./example_vids/dogs_small.mp4', show=False, conf=0.4, stream=True)  # detect video stream

        for result in results:
                # if not len(result.boxes) > 0 and not tensor(16.) in result.boxes.cls:
                
                if not len(result.boxes) > 0:
                        continue
                if not tensor(16.) in result.boxes.cls:
                        continue
                cropped_images = construct_cropped_images(result.boxes, result.orig_img)
                confidences = list(zip(
                        result.boxes.cls,
                        result.boxes.conf
                ))
                yield confidences, result.boxes, cropped_images
                                
if __name__ == "__main__":
        for confidences, boxes, cropped_image in generate_predictions():
                print("Confidences: ", confidences)
                print("Boxes: ", boxes)
                print("Cropped Image: ", cropped_image)
                print("---------------------------------------------------")