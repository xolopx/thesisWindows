import argparse
import threading
import cv2 as cv
from detection import *
from webapp import customApp
from webapp.streamer import detect_motion

if __name__ == '__main__':

    # Reading in Arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
                    help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
                    help="# of frames used to construct the background model")
    args = vars(ap.parse_args())

    # Initializing detection
    inputVideo = cv.VideoCapture(r"C:\Users\Tom\Desktop\thesisWindows\System\detection\traffic_short.mp4")      # Grab the video
    process = CVModule.CVModule(inputVideo)                                                                     # Create the computer vision module.

    # Commencing threads
    t1 = threading.Thread(target=process.process)     # This thread runs method detect_motion().
    t1.daemon = True                                    # Means that all threads stop when this one does.
    t1.start()                                          # Start the thread.
    print("Started Detection Thread")

    t2 = threading.Thread(target=detect_motion)
    t2.daemon = True
    t2.start()
    print("Started Web Cam")

customApp.run(host=args["ip"], port=args["port"], debug=True,
        threaded=True, use_reloader=False)
print("Started Streaming Service")