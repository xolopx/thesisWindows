from webapp import customApp, db
from flask import Response, render_template

import imutils
import cv2
import threading
import argparse
import datetime

outputFrame = db.currentFrame   # Creates reference to current frame from Glob database so that both Flask and detector must share it.
lock = db.lock                  # Creates reference to lock from Glob so that both Flask and detector share same lock.
vs = cv2.VideoCapture(0)        # Initialize video capture stream.


# Retrieves the rendered html page
@customApp.route("/")
def index():
    return render_template("index.html")


def detect_motion():
    global vs, outputFrame, lock
    total = 0
    while True:
        # frame = vs.read()
        frame = db.currentFrame     # Get current frame from db.

        if frame is not None:
            cv2.imshow('', frame)
            cv2.waitKey(1)

            frame = imutils.resize(frame, width=400)
            timestamp = datetime.datetime.now()
            cv2.putText(frame, timestamp.strftime(
                "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            total += 1

            outputFrame = frame.copy()


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock
    # loop over frames from the output stream
    # Each time yield is reached the function returns a generator.
    while True:
        # wait until the lock is acquired
        # with lock:
            # lock.acquire()
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
            # lock.release()
        # yield the output frame in the byte format. This returns a generator.
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')


@customApp.route("/video_feed")
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
    customApp.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)
# release the video stream pointer
# vs.stop()