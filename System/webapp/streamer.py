# import the necessary packages
from webapp import app
from imutils.video import VideoStream
from flask import Response, Flask, render_template

import imutils
import cv2
import threading
import argparse
import datetime
import time

outputFrame = None  # Initialize outputFrame
lock = threading.Lock()  # Initialize lock
vs = VideoStream(src=0).start()  # Start the video stream
time.sleep(2.0)  # Give it time to initialize


# Retrieves the rendered html page
@app.route("/")
def index():
    # print("call to index")
    # return the rendered template
    return render_template("index.html")


def detect_motion():
    # grab global references to the video stream, output frame, and
    # lock variables
    global vs, outputFrame, lock
    # initialize the motion detector and the total number of frames
    # read thus far
    # md = SingleMotionDetector(accumWeight=0.1)
    total = 0
    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=400)
        timestamp = datetime.datetime.now()
        cv2.putText(frame, timestamp.strftime(
            "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        total += 1
        with lock:
            # print("Stuck in Detect Motion \n")
            outputFrame = frame.copy()


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock
    # loop over frames from the output stream
    # Each time yield is reached the function returns a generator.
    while True:
        # wait until the lock is acquired
        with lock:
            # print("Stuck in Generate() \n")
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format. This returns a generator.
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    # print("Updating feed\n")
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


# check to see if this is the main thread of execution
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
                    help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
                    help="# of frames used to construct the background model")
    args = vars(ap.parse_args())
    # start a thread that will perform motion detection
    t = threading.Thread(target=detect_motion)
    t.daemon = True
    t.start()
    # detect_motion()
    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)
# release the video stream pointer
vs.stop()