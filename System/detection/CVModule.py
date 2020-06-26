import math
import re
import globals
import cv2 as cv
import numpy as np
from datetime import datetime
import database_interface as db
from detection import CentroidTracker, TrackableObject, Line, Point

class CVModule:
    """
    Handles the detection, tracking, counting and speed estimation of an object given a
    series of images.
    """

    def __init__(self,rotate_code, inputVideo, params, id, lat, long):
        """
        A CVModule Object controls the configuration of the detection algorithm and executes the
        algorithm on the input video. It then sends the statistics derived from the input to the
        database.

        :param inputVideo:
        :param param: Dictionary of configurations and node info for algorithm instance.
        """
        self.tracked_objects = {}
        self.countNegative = 0
        self.countPositive = 0
        self.frameCount = 0
        self.params = params
        self.video = inputVideo
        self.rotate_code = rotate_code
        self.time = datetime.now()
        self.count_line1 = Line.Line(self.parse_point(self.params["count_line1_p1"]),self.parse_point(self.params["count_line1_p2"]))
        self.count_line2 = Line.Line(self.parse_point(self.params["count_line2_p1"]),self.parse_point(self.params["count_line2_p2"]))
        self.centroidTracker = CentroidTracker.CentroidTracker(maxDisappeared= int(self.params["missing"]), maxDistance= int(self.params["max_dist"]), minDistance=int(self.params["min_dist"]))
        if self.params["live"] == "True":
            self.totalFrames = math.inf
        else:
            self.totalFrames = self.video.get(cv.CAP_PROP_FRAME_COUNT)
        self.subtractor = cv.createBackgroundSubtractorMOG2(history = int(params["history"]), detectShadows= bool(params["shadows"]))
        self.wait = int(self.params["frame_wait"])
        self.countNegativeCurrent = 0
        self.countPositiveCurrent = 0

    def process(self):
        global image

        if self.params["training"] == "True":
            self.train_subtractor()
        # Initializing a timer that is used to measure if a statistics interval has passed.
        timerStart = datetime.now()
        # # Make sure the node is in the database. *** HANDLED IN MAIN ***
        # db.insert.insert_node(self.id, "Node001", "West", self.longitude, self.latitude)
        """ MAIN LOOP """
        # Loop will execute until all input processed or user exits.
        while True and self.frameCount < (self.totalFrames - int(self.params["history"])):
            # Read a frame of input video.
            _, frame = self.video.read()

            # check if the frame needs to be rotated
            if self.rotate_code == 180:
                frame = cv.rotate(frame, cv.ROTATE_180)

            frame = self.resize_frame(frame)
            # Apply the subtractor to the frame to get foreground objects.
            mask = self.subtractor.apply(frame)
            # Apply morphology, threshing and median filter.
            mask = self.filter_frame(mask)
            # Get bounding boxes for the foreground objects.
            contours, boundingRect = self.define_contours(mask)
            # Get centroids from the bounding boxes.
            self.centroidTracker.update(boundingRect)
            # Update the object positions and vehicle statistics.
            self.update_tracked_objects()
            # Convert foreground mask back to a 3-channel image.
            mask = cv.cvtColor(mask, cv.COLOR_GRAY2RGB)
            # Draw graphics
            if self.params["graphics"] == "True":
                self.draw_graphics(mask, boundingRect)
                self.draw_graphics(frame, boundingRect)
            # Stitch together original image and foreground mask for display.
            combined = np.hstack((frame, mask))
            # Updating the frame shared with Flask app.
            globals.image = combined
            # Increment the number of frames.
            self.frameCount += 1
            # Perform speed measurements                            *** PUT THIS IN A METHOD *** ALSO FIX THE SPEED CALCULATION SO THEY WORK ****
            if self.frameCount % 1 == 0:
                for objID, objs in self.tracked_objects.items():
                    objs.calc_speed()

            # Log statistics   *** CURRENTLY TURNED OFF ***
            if(self.params["log_stats"]) == "True":
                timerStart = self.log_stats(timerStart, int(self.params["storage_interval"]))

            if self.params["live"] != "True":
                if (self.frameCount >= (self.totalFrames - int(self.params["history"]))):
                    # Reset frame count.
                    self.frameCount = 0
                    # Reset video cursor.
                    self.video.set(cv.CAP_PROP_POS_FRAMES, 0)

            # Show the result.
            cv.imshow("Frame", frame)
            cv.imshow("Mask", mask)


            if self.params["rapid_test"] != "True":
                while True:
                    key = cv.waitKey(self.wait-10)
                    if key == ord('n'):
                        break
            else:
                cv.waitKey(int(self.params["frame_wait"]))

            if self.params["live"] == "True":
                if int(self.params["test_length"]) > 0:
                    if(self.frameCount == int(self.params["test_length"])):
                        while True:
                            key = cv.waitKey(10)
                            if key == ord("q"):
                                break

    def train_subtractor(self):
        """
        Trains subtractor on the first N frames of video so it has a better idea
        of what the background consists of.
        :param trainNum: Number of training frames to be used on the model.
        """

        i = 0
        while i < int(self.params["history"]):
            _, frame = self.video.read()

            # check if the frame needs to be rotated
            if self.rotate_code == 180:
                frame = cv.rotate(frame, cv.ROTATE_180)

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

    def update_tracked_objects(self):
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
                if self.params["traffic_orientation"] == "True":
                    motion = [c[1] for c in tracked_object.centroids]
                    motion = centroid[1] - np.mean(motion)
                else:
                    motion = [c[0] for c in tracked_object.centroids]
                    motion = centroid[0] - np.mean(motion)

                if motion > 0:      # X-values get larger left to right.
                    motion = True
                else:
                    motion = False

                # Determine which line object should be checked against.
                if int(self.params["num_lines"]) > 1:
                    line = self.which_line(tracked_object)
                else:
                    line = True

                # Append new centroid to tracked object history.
                tracked_object.centroids.append(centroid)

                # Count vehicle's that haven't been counted and have crossed line with requisite position history length.
                if not tracked_object.counted and len(tracked_object.centroids) > int(self.params["history_count"]) \
                    and self.check_track_crossing(centroid, motion, line) and self.check_start_pos(motion, tracked_object, line):

                    if motion:
                        self.countPositive += 1
                        self.countPositiveCurrent += 1
                        tracked_object.counted = True

                        if self.params["print_positive"] == "True":
                            if self.params["traffic_orientation"] == "True":
                                print("Down + ID {}".format(tracked_object.objectID))
                            else:
                                print("Right + ID {}".format(tracked_object.objectID))
                    else:
                        self.countNegative += 1
                        self.countNegativeCurrent += 1
                        tracked_object.counted = True

                        if self.params["print_negative"] == "True":
                            if self.params["traffic_orientation"] == "True":
                                print("Up + ID {}".format(tracked_object.objectID))
                            else:
                                print("Left + ID {}".format(tracked_object.objectID))


            # Else create a new trackable object for the centroid.l
            else:
                tracked_object = TrackableObject.TrackableObject(objectID, centroid, self.frameCount)
                self.tracked_objects[objectID] = tracked_object

        # Delete tracked objects if their centroid has been deregistered.
        for ID in self.centroidTracker.deregisteredID:
            del self.tracked_objects[ID]
        self.centroidTracker.deregisteredID.clear()

    def check_start_pos(self, motion, trackedObject, line):
        """
        Checks that an object started on the other side of the count line to where it's being counted.
        :param line: Determines which line to check against.
        :param trackedObject: Object that's going to be counted.
        :param motion: Indicates the direction of travel of an object.
        """
        count = 0
        if line:
            line = self.count_line1
        else:
            line = self.count_line2

        # Check how many centroids started on the other side of the line.
        for centroid in trackedObject.centroids:
            # The motion should be opposite to the side the object started on for it to count.
            if self.pt_rel(line, Point.Point(centroid[0],centroid[1])) != motion:
                count += 1
        return count > int(self.params["otherside_centroids"])

    def check_track_crossing(self, centroid, motion, line):
        """
        Checks if a vehicle has crossed the count_line. Determines which count line by looking at orientation and line end
        points to see if object lays between them.
        :param line: True if use line one, False if use line two.
        :param centroid: The point specifying the centroid's location.
        :param motion: Specifies direction that traffic is moving. True if up and down, False is side to side.
        :return:
        """
        if line:
            line = self.count_line1
        else:
            line = self.count_line2

        # Create a point for the centroid
        cen_p = Point.Point(centroid[0], centroid[1])
        # Check points position relative to the line. True is above, False is below.
        pos = self.pt_rel(line, cen_p)
        # True if position is side matching direction of travel.
        return (pos == motion)

    def which_line(self, tracked_object):
        """
        Determines which line a tracked object should be measured against by checking it's average position.
        :return: True for line1 and False for line2
        """

        # If orientation True check between x values. If orientation False check between y values.
        # Get average position of tracked_object in axis according to orientation.
        if self.params["traffic_orientation"] == "True":
            av_x = np.mean([c[0] for c in tracked_object.centroids])

            # Protecting against weird order of points in config_file.
            if self.count_line1.p1.x <= self.count_line1.p2.x:
                l1_x1 = self.count_line1.p1.x
                l1_x2 = self.count_line1.p2.x
            else:
                l1_x1 = self.count_line1.p2.x
                l1_x2 = self.count_line1.p1.x

            if self.count_line2.p1.x <= self.count_line2.p2.x:
                l2_x1 = self.count_line2.p1.x
                l2_x2 = self.count_line2.p2.x
            else:
                l2_x1 = self.count_line2.p2.x
                l2_x2 = self.count_line2.p1.x

            # Blob is between line one.
            if l1_x1 <= av_x <= l1_x2:
                return True
            # Blob is between line two.
            elif l2_x1 <= av_x <= l2_x2:
                return False
            # Houston we have a problem.
            else:
                raise(Exception("Your vehicles don't lay between your lines somehow, panic!"))

        else:
            av_y = np.mean([c[1] for c in tracked_object.centroids])
            # Protecting against weird order of points in config_file.
            if self.count_line1.p1.y <= self.count_line1.p2.y:
                l1_y1 = self.count_line1.p1.y
                l1_y2 = self.count_line1.p2.y
            else:
                l1_y1 = self.count_line1.p2.y
                l1_y2 = self.count_line1.p1.y

            if self.count_line2.p1.y <= self.count_line2.p2.y:
                l2_y1 = self.count_line2.p1.y
                l2_y2 = self.count_line2.p2.y
            else:
                l2_y1 = self.count_line2.p2.y
                l2_y2 = self.count_line2.p1.y

            # Blob is between line one.
            if l1_y1 <= av_y <= l1_y2:
                return True
            # Blob in between line two.
            elif l2_y1 <= av_y <= l2_y2:
                return False
            # Houston we have a problem.
            else:
                raise (Exception("Your vehicles don't lay between your lines somehow, panic!"))

    def parse_point(self, pt_string):
        """ Returns a point from a string of the format (x,y)
        :param pt_string: String of the form (x,y).
        :return: The Point made of the data extracted from the string.
        """
        # Use regex to parse numbers from string
        num_list = re.findall("\d+",pt_string)
        # Gets the two numbers out of the string
        return Point.Point(int(num_list[0]), int(num_list[1]))

    def pt_rel(self, l, pt):
        """
        Checks if a point is above or below a line.
        :param l: Line
        :param pt: Point
        :return: True if point is on or below the line, False otherwise.
        """
        if math.isinf(l.m):
            if pt.x >= l.p1.x:
                return True
            else:
                return False
        else:
            if pt.y >= l.m*pt.x + l.b:
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

            if self.params["multilane"] == "True":
                db.insert.insert_count_minute(self.countNegativeCurrent,timerStart, 0, 0)
                db.insert.insert_count_minute(self.countPositiveCurrent,timerStart, 0, 1)
            else:
                # Direction True means positive
                if self.params["singlelane"] == "True":
                    db.insert.insert_count_minute(self.countPositiveCurrent, timerStart, 0, 1)
                # Else direction is negative.
                else:
                    db.insert.insert_count_minute(self.countNegativeCurrent, timerStart, 0, 0)

            self.countNegativeCurrent = 0
            self.countPositiveCurrent = 0

            # Reset the displayed count.
            if self.params["refresh_count"] == "True":
                self.countNegative = 0
                self.countPositive = 0
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

        if self.params["boxes"] == "True":
            # Draw bounding boxes.
            for i in range(len(boxes)):
                cv.rectangle(image, (int(boxes[i][0]), int(boxes[i][1])), (int(boxes[i][0] + boxes[i][2]), int(boxes[i][1] + boxes[i][3])), (0, 255, 238), 2)
                text = "({},{})".format(int(boxes[i][2]), int(boxes[i][3]))
                cv.putText(image, text, (boxes[i][0] - 10, boxes[i][1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        if self.params["centroids"] == "True":
            # Draw Centroids
            for i, (objectID, centroid) in enumerate(self.centroidTracker.centroids.items()):
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

        if self.params["count_line"] == "True":
            if int(self.params["num_lines"]) == 1:
                # Draw lines
                p1 = self.count_line1.p1
                p2 = self.count_line1.p2
                cv.line(image, (p1.x, p1.y), (p2.x, p2.y), (255, 1, 255), 2)
            else:
                # Draw lines
                l1_p1 = self.count_line1.p1
                l1_p2 = self.count_line1.p2
                l2_p1 = self.count_line2.p1
                l2_p2 = self.count_line2.p2
                cv.line(image, (l1_p1.x, l1_p1.y), (l1_p2.x, l1_p2.y), (255, 1, 255), 2)
                cv.line(image, (l2_p1.x, l2_p1.y), (l2_p2.x, l2_p2.y), (255, 1, 255), 2)

        # Draw Counts
        if self.params["count_graphics"] == "True":

            if self.params["traffic_orientation"] == "True":
                str1 = "Up {}"
                str2 = "Down {}"
            else:
                str1 = "Left {}"
                str2 = "Right {}"

            p1 = self.parse_point(self.params["pos_pos"])
            p2 = self.parse_point(self.params["neg_pos"])

            textUp = str1.format(self.countNegative)
            textDown = str2.format(self.countPositive)
            cv.putText(image, textUp, (p1.x, p1.y), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
            cv.putText(image, textDown, (p2.x, p2.y), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)



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

        if self.params["frame_count"] == "True":
            cv.putText(image, "Wait: {} Frame: {}".format(self.wait, self.frameCount), (280, 30),cv.FONT_HERSHEY_SIMPLEX, 0.5, (224, 9, 52, 2))

        if self.params["grid"] == "True":
            self.draw_grid(image)

    def draw_grid(self,image):

        across = 0
        up = 0
        for i in range(image.shape[0] % 50):
            cv.line(image,(0,across),(int(image.shape[1]),across), (66, 135, 245), 1)
            across += 50

        for i in range(image.shape[1] % 50):
            cv.line(image,(up,0),(up,int(image.shape[0])), (66, 135, 245), 1)
            up += 50

    def resize_frame(self, img):

        scale_percent = int(self.params["scale_percent"])
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        img = cv.resize(img, dim, interpolation=cv.INTER_AREA)
        return img