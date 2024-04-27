# detection-service
YOLO detection service for classifying dogs


## Setup

1. Create a python venv for the sake of your sanity.
   1. `python -m venv .venv`
2. Activate the venv (do this anytime you wanna run it too)
   1. `source .venv/bin/activate`
3. install dependencies
   1. `pip install -r requirements.txt`
2. Edit the config file if necessary. 
   1. Most importantly make sure app_host and app_port match the values used in dogfinder-app

## Running

1. Activate the venv as above
   1. `source .venv/bin/activate`
   2. In vscode you can have this done automatically. 
2. Run the program
   1. `python main.py`
