import cv2 as cv
from detection import *
from flask import Response, render_template, Flask
from threading import Event
import imutils
import cv2
import threading
import argparse
import datetime


outputFrame = None
someOtherFrame = None
lock = threading.Lock()
vs = cv2.VideoCapture(0)        # Initialize video capture stream.
event = Event()
app = Flask(__name__)

def detect_motion():
    global outputFrame
    total = 0
    # might need to put the lock in here.
    while True:
        _, frame = vs.read()

        if frame is not None:


            frame = imutils.resize(frame, width=400)
            timestamp = datetime.datetime.now()
            cv2.putText(frame, timestamp.strftime(
                "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            total += 1
            outputFrame = frame.copy()

def generate():
    global outputFrame
    while True:
        if outputFrame is None:
            continue
        (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
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

if __name__ == '__main__':

    args = argumentRead()

    inputVideo = cv.VideoCapture(r"C:\Users\Tom\Desktop\thesisWindows\System\detection\traffic_short.mp4")      # Grab the video
    process = CVModule.CVModule(inputVideo)                                                                     # Create the computer vision module.

    t2 = threading.Thread(target=process.process)                                                               # This thread runs method detect_motion().
    t2.daemon = True                                                                                            # Means that all threads stop when this one does.
    t2.start()                                                                                                  # Start the thread.
    print("Training Detection")

    t1 = threading.Thread(target=detect_motion)  # This thread runs method detect_motion().
    t1.daemon = True  # Means that all threads stop when this one does.
    t1.start()  # Start the thread.
    print("Started App loop")

    app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)

