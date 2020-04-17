import cv2 as cv

from detection import CVModule

inputVideo = cv.VideoCapture(r"C:\Users\Tom\Desktop\thesisWindows\System\traffic_short.mp4")
process = CVModule.CVModule(inputVideo)
process.process()



