""" Written for the purpose of testing this system submodule."""
import cv2 as cv
from detection import *


# Detection
inputVideo = cv.VideoCapture(r"C:\Users\Tom\Desktop\thesisWindows\System\detection\traffic_short.mp4")
process = CVModule.CVModule(inputVideo)
process.process()
