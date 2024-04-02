from torch import tensor
from ultralytics import YOLO
import cv2
from uuid import uuid4


def construct_cropped_image(box, original_image):
        xyxy_format = box.xyxy[0]

        x1, y1 = xyxy_format[0], xyxy_format[1]
        x2, y2 = xyxy_format[2], xyxy_format[3]

        cropped_image = original_image[int(y1):int(y2), int(x1):int(x2)]
        image_name = f"cropped_image_{str(uuid4())}.jpg"

        cv2.imwrite("./output_images/" + image_name, cropped_image)

        return image_name


# def process_results(result):
#         detected_dogs = [
#             box for box in result.boxes if box.cls == tensor([16.])
#         ]

#         cropped_images = [
#             construct_cropped_image(box, result.orig_img)
#             for box in detected_dogs
#         ]

#         return cropped_images


def process_boxes(boxes, original_image):

        if len(boxes) == 0:
                return []
        cropped_images = [
            construct_cropped_image(box, original_image) for box in boxes
        ]

        return cropped_images


# Convert the tensor IDs into integers for comparison
def generate_integer_ids(tensor_ids):
        for tensor_id in tensor_ids:
                yield int(tensor_id)


def generate_prediction_images(model_name="yolov8n.pt",
                               video_source='./example_vids/dogs_small.mp4'):

        model = YOLO(model_name)
        results = model(source=video_source, show=False, conf=0.4, stream=True)
        tracked_results = model.track(source=video_source,
                                      show=False,
                                      conf=0.4,
                                      stream=True,
                                      iou=0.5)

        unique_ids = set()

        for result in tracked_results:

                # print("RESULT", result.boxes)
                print("Unique IDs", unique_ids)

                # Sometimes there is no id for the boxes not sure why
                if result.boxes.id is None:
                        continue

                # Check if there are any boxes detected in the frame
                if not len(result.boxes) > 0:
                        continue

                # Check if there is a dog detected in the frame
                # 16 is the class id for dogs
                if not tensor(16.) in result.boxes.cls:
                        continue

                boxes_to_process = []

                for index, id in enumerate(generate_integer_ids(result.boxes.id)):
                        
                        if id in unique_ids:
                                continue
                        
                        unique_ids.add(id)
                        boxes_to_process.append(result.boxes[index])
                        
                yield process_boxes(boxes_to_process, result.orig_img)


if __name__ == '__main__':
        for cropped_images in generate_prediction_images():
                print(cropped_images)
                print("done")
