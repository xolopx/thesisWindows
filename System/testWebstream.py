from webapp.streamer import detect_motion
from webapp import customApp
import threading
import argparse

# Reading in Arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--ip", type=str, required=True,
                help="ip address of the device")
ap.add_argument("-o", "--port", type=int, required=True,
                help="ephemeral port number of the server (1024 to 65535)")
ap.add_argument("-f", "--frame-count", type=int, default=32,
                help="# of frames used to construct the background model")
args = vars(ap.parse_args())

t2 = threading.Thread(target=detect_motion)
t2.daemon = True
t2.start()

customApp.run(host=args["ip"], port=args["port"], debug=True,
        threaded=True, use_reloader=False)


