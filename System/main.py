import cv2 as cv
from detection import *
from flask import Response, render_template, Flask
from threading import Event
import imutils
import cv2
import threading
import argparse
import datetime
import globals
import database_interface as db


globals.initialize()
# outputFrame = None
someOtherFrame = None
lock = threading.Lock()
vs = cv2.VideoCapture(r"C:\Users\Tom\Desktop\thesisWindows\System\detection\traffic_short.mp4")        # Initialize video capture stream.
# vs = cv2.VideoCapture(0)        # Initialize video capture stream.
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

    # Try to add a node
    # update_or_add_node()
    db.delete.delete_node(0)
    # Try to read back node that's been added
    # retrieve_node()



    #
    inputVideo = cv.VideoCapture(r"C:\Users\Tom\Desktop\thesisWindows\System\detection\traffic_short.mp4")      # Grab the video
    process = CVModule.CVModule(inputVideo)                                                                     # Create the computer vision module.

    t2 = threading.Thread(target=process.process)                                                               # This thread runs method detect_motion().
    t2.daemon = True                                                                                            # Means that all threads stop when this one does.
    t2.start()                                                                                                  # Start the thread.
    print("Training Detection")

    app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)


