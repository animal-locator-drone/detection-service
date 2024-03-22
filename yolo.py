from ultralytics import YOLO


def main():

    model = YOLO("yolov8n.pt")  # initialize model
    # results = model(source=0, show=True, conf=0.4, save=False) # run model on webcam stream
    results = model.train(
        data="/Volumes/X9 Pro/CS/SeniorProj/Data/wolf.v11i.yolov8/data.yaml",  # must modify to appropriate path # ideally everyone has their custom yaml in their pwd
        epochs=3,
        device="mps",  # mac m-series(apple silicon)ONLY optimization parameter
    )


def train_model():
    pass


if __name__ == "__main__":
    main()
