from detection import *
from flask import Response, render_template, Flask
from threading import Event
import cv2
import threading
import argparse
import globals
import database_interface as db
import os

globals.initialize()
# outputFrame = None
someOtherFrame = None
lock = threading.Lock()
event = Event()
app = Flask(__name__)

def generate():
    # global outputFrame
    print('Got image in web-server')
    while True:
        if globals.image is None:
            continue
        (flag, encodedImage) = cv2.imencode(".jpg", globals.image)
        if not flag:
            continue
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/")
def index():
    return render_template("index.html")

def argumentRead():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
                    help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
                    help="# of frames used to construct the background model")
    args = vars(ap.parse_args())
    return args

def update_or_add_node():
    """ Checks and updates the node's profile in the database. Creates a new entry if
        it doesn't exist in the database.
        """

    # This is dummy data for now.
    node_name = "Node001"
    id = 0
    location = "King St"
    perspective = "West"
    latitude = 10
    longitude = 10

    # Attempt update
    if db.query.node_exists(id):
        print ('Entry Exists So Update.')
        db.update.update_node(id, node_name, perspective, longitude, latitude)
    else:
        print('Entry Not Found So Create New')
        db.insert.insert_node(id, node_name, perspective, longitude, latitude)

if __name__ == '__main__':

    globals.initialize()
    args = argumentRead()

    # Instantiate Detection Module
    # inputVideo = cv.VideoCapture(r"C:\Users\Tom\Desktop\thesisWindows\System\detection\traffic_short.mp4")
    # inputVideo = cv2.VideoCapture(r"C:\Users\Tom\Desktop\merging.mp4")
    # inputVideo = cv.VideoCapture(0)


    dirname = os.path.dirname(__file__)
    config_path = os.path.join(dirname, r'config_files\live1.txt')

    video_path = r"C:\Users\Tom\OneDrive - The University Of Newcastle\FYP\video_data\1.mp4"
    # video_path = r"C:\Users\c3175\OneDrive - The University Of Newcastle\FYP\video_data\3.mp4"

    config_parser = ConfigParser.ConfigParser(config_path)
    config_parser.parseConfig()
    rotate = int(config_parser.parameters["rotate"])

    if (config_parser.parameters["live"] == "True"):
        inputVideo = cv2.VideoCapture(0)
    else:
        inputVideo = cv2.VideoCapture(video_path)  # Initialize video capture stream.

    process = CVModule.CVModule(rotate, inputVideo, config_parser.parameters, id=0, lat=10, long=10)

    update_or_add_node()

    # Start detection thread
    t2 = threading.Thread(target=process.process)
    t2.daemon = True
    t2.start()
    print("Training Detection")

    app.run(port=args["port"], debug=True,
            threaded=True, use_reloader=False)
    # app.run(debug=True,
    #         threaded=True, use_reloader=False)

