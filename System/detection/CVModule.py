import re
import globals
import cv2 as cv
import numpy as np
from datetime import datetime
import database_interface as db
import sympy.geometry as sym
from detection import CentroidTracker, TrackableObject, ConfigParser, Line, Point





class CVModule:
    """
    Handles the detection, tracking, counting and speed estimation of an object given a
    series of images.
    """

    def __init__(self, inputVideo, params, id, lat, long):
        """
        A CVModule Object controls the configuration of the detection algorithm and executes the
        algorithm on the input video. It then sends the statistics derived from the input to the
        database.

        :param inputVideo:
        :param param: Dictionary of configurations and node info for algorithm instance.
        """
        self.tracked_objects = {}
        self.countUp = 0
        self.countDown = 0
        self.frameCount = 0
        self.params = params
        self.video = inputVideo
        self.time = datetime.now()
        # Orientation of traffic. True is up/down, False is left/right.
        self.orientation = bool(self.params["traffic_orientation"])
        self.count_line = Line.Line(self.parse_point(self.params["count_line_p1"]),self.parse_point(self.params["count_line_p2"]))
        self.centroidTracker = CentroidTracker.CentroidTracker(maxDisappeared= int(self.params["missing"]), maxDistance= int(self.params["max_dist"]), minDistance=int(self.params["min_dist"]))
        self.totalFrames = self.video.get(cv.CAP_PROP_FRAME_COUNT)
        self.subtractor = cv.createBackgroundSubtractorMOG2(history = int(params["history"]), detectShadows= bool(params["shadows"]))

    def process(self):
        global image

        # self.train_subtractor()
        # Initializing a timer that is used to measure if a statistics interval has passed.
        timerStart = datetime.now()
        # # Make sure the node is in the database. *** HANDLED IN MAIN ***
        # db.insert.insert_node(self.id, "Node001", "West", self.longitude, self.latitude)

        """ MAIN LOOP """
        while True and self.frameCount < (self.totalFrames - int(self.params["history"])):  # Loop will execute until all input processed or user exits.
            # Read a frame of input video.
            _, frame = self.video.read()
            frame = self.resize_frame(frame)
            # Apply the subtractor to the frame to get foreground objects.
            mask = self.subtractor.apply(frame)
            # Apply morphology, threshing and median filter.
            mask = self.filter_frame(mask)
            # Get bounding boxes for the foreground objects.
            contours, boundingRect = self.define_contours(mask)
            # Get centroids from the bounding boxes.                *** LOOK INTO WHAT THIS METHOD IS DOING AND IF IT'S NECESSARY ***
            self.centroidTracker.update(boundingRect)
            # Update the object positions and vehicle statistics.   *** MAYBE WANT TO SEPARATE THIS INTO TWO METHODS ***
            self.speed_count_check()
            # Convert foreground mask back to a 3-channel image.
            mask = cv.cvtColor(mask, cv.COLOR_GRAY2RGB)
            # Draw graphics onto mask
            self.draw_graphics(mask, boundingRect)
            # Draw graphics onto original frame
            self.draw_graphics(frame, boundingRect)
            # Stitch together original image and foreground mask for display.
            combined = np.hstack((frame, mask))
            # Updating the frame shared with Flask app.
            globals.image = frame
            # Increment the number of frames.
            self.frameCount += 1
            # Perform speed measurements                            *** PUT THIS IN A METHOD *** ALSO FIX THE SPEED CALCULATION SO THEY WORK ****
            if self.frameCount % 1 == 0:
                for objID, objs in self.tracked_objects.items():
                    objs.calc_speed()

            # Log statistics   *** CURRENTLY TURNED OFF ***
            timerStart = self.log_stats(timerStart, 3)

            # *** TESTING: FOR CONTROLLING SPEED OF VIDEO AND PAUSING VIDEO ***
            key = cv.waitKey(33)
            if key == 27:
                break
            if key == ord('n'):
                while True:
                    key = cv.waitKey(50)
                    if key == ord('n'):
                        break

            # *** TESTING: LOOPING LOGIC JUST FOR TESTING WITH SHORT VIDEO ***
            if (self.frameCount >= (self.totalFrames - 600)):
                # Reset frame count.
                self.frameCount = 0
                # Reset video cursor.
                self.video.set(cv.CAP_PROP_POS_FRAMES, 0)

            # Show the result.
            cv.imshow("Combined", combined)

    def train_subtractor(self, trainNum=500):
        """
        Trains subtractor on the first N frames of video so it has a better idea
        of what the background consists of.
        :param trainNum: Number of training frames to be used on the model.
        """

        i = 0
        while i < trainNum:
            _, frame = self.video.read()
            self.subtractor.apply(frame, None, 0.001)
            i += 1

    def filter_frame(self,fgMask):
        """
        Applies morphology and median filtering to subtracted image to consolidate foreground objects
        and remove noise.

        :param fgMask: Binary mask that is the output of the subtractor.
        """
        # Get configurations
        size = int(self.params["morph_size"])
        shape = int(self.params["morph_shape"])
        iter = int(self.params["morph_iter"])
        med_size = int(self.params["med_size"])

        # Structuring element for morphological operations. Rect: 0, Cross:1, Ellipse:2
        struct = cv.getStructuringElement(shape, (size,size))
        # Threshold out shadows. (They're darker colored than pure foreground).
        fgMask[fgMask < 240] = 0
        # Apply median blur filter to remove salt and pepper noise.
        fgMask = cv.medianBlur(fgMask,med_size)
        # Apply a closing to the surviving foreground blobs.
        fgMask = cv.morphologyEx(fgMask, cv.MORPH_CLOSE, struct, iterations = iter)
        # Apply dilation tracked_object embolden the foreground objects.
        fgMask = cv.dilate(fgMask, struct, iterations= iter)

        return fgMask

    def define_contours(self, fgMask):
        # Look for contours in the foreground mask.
        contours, _ = cv.findContours(fgMask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        # Create list to hold contour best rectangle fits.
        boundRect = []

        min_w = int(self.params["min_width"])
        min_h = int(self.params["min_height"])
        max_w = int(self.params["max_width"])
        max_h = int(self.params["max_height"])

        # Move through contours list generating enumerated pairs (indice, value).
        for i, c in enumerate(contours):
            # Generate bounding rect from the poly-form contrackObject. Returns "Upright Rectangle", i.e. Axis-aligned on bot track Obj edge and whose left edge is vertical.
            (x, y, w, h) = cv.boundingRect(c)
            # Thresh bounding box by width and height.
            if max_w >= w >= min_w and max_h >= h >= min_h:
                # Generate bounding rect from the poly-form contrackObject. Returns "Upright Rectangle", i.e. Axis-aligned on bot track Obj edge and whose left edge is vertical.
                boundRect.append(cv.boundingRect(c))
        # Return the bounding rectangles.

        return contours, boundRect

    def speed_count_check(self):
        """ Updates the centroid history of tracked objects and checks if the
            objects have passed speed and count thresholds."""
        # Create a copy of the list of current centroids.
        centroids = self.centroidTracker.centroids

        # Iterate over centroids and check if any have cross over count and speed lines.
        for (objectID, centroid) in centroids.items():
            tracked_object = self.tracked_objects.get(objectID)
            # If there's a tracked object for the centroid then check if it can be counted.
            if tracked_object is not None:
                # If camera orientation portrait check y-direction.
                if self.orientation:
                    motion = [c[1] for c in tracked_object.centroids]
                    motion = centroid[1] - np.mean(motion)
                # Else check x direction.
                else:
                    motion = [c[0] for c in tracked_object.centroids]
                    motion = centroid[0] - np.mean(motion)
                # Set motion to boolean.
                if motion > 0:
                    motion = True
                else:
                    motion = False

                # Append new centroid to tracked object history.
                tracked_object.centroids.append(centroid)

                # only record stats for object if it hasn't already been counted.
                if not tracked_object.counted:
                    if self.check_track_crossing(centroid, motion):
                        self.countUp += 1
                        tracked_object.counted = True
                    elif self.check_track_crossing(centroid, motion):
                        self.countDown += 1
                        tracked_object.counted = True
            # Else create a new trackable object for the centroid.l
            else:
                tracked_object = TrackableObject.TrackableObject(objectID, centroid, self.frameCount)
                self.tracked_objects[objectID] = tracked_object

        # Delete tracked objects if their centroid has been deregistered.
        for ID in self.centroidTracker.deregisteredID:
            del self.tracked_objects[ID]
        self.centroidTracker.deregisteredID.clear()

    def check_track_crossing(self, centroid, motion):
        """
        Checks
        :param centroid: The point specifying the centroid's location.
        :param motion: Specifies direction that traffic is moving. True if up and down, False is side to side.
        :return:
        """
        # Create a point for the centroid
        cen_p = Point.Point(centroid[0], centroid[1])
        # Check points position relative to the line. True is above, False is below.
        pos = self.pt_rel(self.count_line, cen_p)
        # True if position is side matching direction of travel.
        return (pos != motion)

    def parse_point(self, pt_string):
        """ Returns a point from a string of the format (x,y)
        :param pt_string: String of the form (x,y).
        :return: The Point made of the data extracted from the string.
        """
        # Use regex to parse numbers from string
        num_list = re.findall("\d",pt_string)
        # Gets the two numbers out of the string
        return Point.Point(int(num_list[0]), int(num_list[1]))

    def pt_rel(self, l, pt):
        """
        Checks if a point is above or below a line.
        :param l: Line
        :param pt: Point
        :return: True if point is on or below the line, False otherwise.
        """
        if pt.y >= l.m + l.b:
            return True
        else:
            return False

    def log_stats(self, timerStart, interval):
        """ Handles entering vehicle count and speed data into the database.
        :param timerStart: The start time of the timer which is used to measure if an interval has passed.
        :param interval: The amount of time between storing a new reading. Measured in seconds.
        """

        # If time interval has passed.
        if (datetime.now() - timerStart).total_seconds() >= interval:
            # Store the readings in the database
            # db.insert.insert_count_minute(self.countUp,timerStart.strftime('%Y-%m-%d %H:%M:%S'),self.id)
            db.insert.insert_count_minute(self.countUp,timerStart,0)
            # Reset the count
            self.countUp = 0
            # Return the new time to the timer.
            return datetime.now()
        else:
            # Return the timer that was passed in.
            return timerStart

    def draw_graphics(self, image, boxes):
        """
        Marks frame count, up & down count, object speed, centroid and bounding boxes on a given image.
        :param image: Image to be drawn on.
        :param boxes: Bounding box information.
        """

        # Draw on the bounding boxes.
        for i in range(len(boxes)):
            cv.rectangle(image, (int(boxes[i][0]), int(boxes[i][1])), (int(boxes[i][0] + boxes[i][2]), int(boxes[i][1] + boxes[i][3])), (0, 255, 238), 2)
        for (objectID, centroid) in self.centroidTracker.centroids.items():
            text = "ID {}".format(objectID)
            cv.putText(image, text, (centroid[0] - 10, centroid[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv.circle(image, (centroid[0], centroid[1]), 4, (0,355, 0),-1)

        # Draw Rectangle
        # imcopy = image.copy()
        # cv.rectangle(imcopy,(0, 380), (1280, 719), (255, 1, 255), -1)
        # cv.line(imcopy, (0, 380), (1280, 380), (10, 118, 242), 2)
        # cv.line(imcopy, (0, 465), (1280, 465), (10, 118, 242), 2)
        # cv.line(imcopy, (0, 550), (1280, 550), (10, 118, 242), 2)
        # cv.line(imcopy, (0, 635), (1280, 635), (10, 118, 242), 2)
        # cv.line(imcopy, (0, 719), (1280, 719), (10, 118, 242), 2)
        # alpha = 0.5
        # cv.addWeighted(imcopy, alpha, image, 1- alpha, 0, image)

        # if self.frameCount == 100:
        #     cv.imshow("Image", image)
        #     cv.waitKey(0)


        # Draw lines
        p1 = self.count_line.p1
        p2 = self.count_line.p2
        cv.line(image, (p1.x, p1.y), (p2.x, p2.y), (255, 1, 255), 2)



        # Draw on counts
        # textUp = "Up {}".format(self.countUp)
        # textDown = "Down {}".format(self.countDown)
        # cv.putText(image, textUp, (50, 50), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
        # cv.putText(image, textDown, (500, 50), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)



        # Add timestamp to the frames.
        # timestamp = datetime.now()
        # cv.putText(image, timestamp.strftime(
        #     "%A %d %B %Y %I:%M:%S%p"), (10, image.shape[0] - 10),
        #            cv.FONT_HERSHEY_SIMPLEX, 0.35, (6, 64, 7), 1)



        # Draw speeds
        for (trackID, track) in self.tracked_objects.items():
            if not track.finished:											# Show speed until object's centroid is deregistered.
                center = track.centroids[-1]								# Get the last centroid in items history.
                x = center[0]
                y = center[1]
                textSpeed = "{:4.2f}".format(track.speed)
                # cv.putText(image, textSpeed, (x-10,y+20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (20, 112, 250), 2)

        # Draw the number of frames
        cv.putText(image, "Frame: {}".format(self.frameCount), (280, 30),cv.FONT_HERSHEY_SIMPLEX, 0.5, (224, 9, 52, 2))
        # self.draw_grid(image)

    def draw_grid(self,image):

        across = 0
        up = 0
        for i in range(image.shape[0] % 50):
            cv.line(image,(0,across),(int(self.width),across), (66, 135, 245), 1)
            across += 50

        for i in range(image.shape[1] % 50):
            cv.line(image,(up,0),(up,int(self.height)), (66, 135, 245), 1)
            up += 50

    def resize_frame(self, img):

        scale_percent = int(self.params["scale_percent"])
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        img = cv.resize(img, dim, interpolation=cv.INTER_AREA)
        return img
