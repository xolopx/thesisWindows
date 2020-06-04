import globals
import cv2 as cv
import numpy as np
from datetime import datetime
import database_interface as db
from detection import CentroidTracker, TrackableObject, ConfigParser





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
        self.tracks = {}
        self.countUp = 0
        self.countDown = 0
        self.frameCount = 0
        self.params = params
        self.video = inputVideo
        self.time = datetime.now()
        self.cenTrack = CentroidTracker.CentroidTracker(maxDisappeared= int(self.params["missing"]), maxDistance= int(self.params["max_dist"]), minDistance=int(self.params["min_dist"]))
        self.totalFrames = self.video.get(cv.CAP_PROP_FRAME_COUNT)
        self.subtractor = cv.createBackgroundSubtractorMOG2(history = int(params["history"]), detectShadows= bool(params["shadows"]))

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
        # Apply dilation trackObj embolden the foreground objects.
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

    def draw_info(self, image, boxes):
        """
        Marks frame count, up & down count, object speed, centroid and bounding boxes on a given image.
        :param image: Image to be drawn on.
        :param boxes: Bounding box information.
        """

        # Draw on the bounding boxes.
        for i in range(len(boxes)):
            cv.rectangle(image, (int(boxes[i][0]), int(boxes[i][1])), (int(boxes[i][0] + boxes[i][2]), int(boxes[i][1] + boxes[i][3])), (0, 255, 238), 2)
        for (objectID, centroid) in self.cenTrack.centroids.items():
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
        # cv.line(image, (0, 340), (640, 340), (255, 1, 255), 2)
        # cv.line(image, (0, 380), (1280, 380), (255, 1, 255), 2)



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
        for (trackID, track) in self.tracks.items():
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

    def update_tracks(self):
        """ Generates and updates trackable objects with centroid data. """
        # Create a copy of centroid dictionary.
        centroids = self.cenTrack.centroids

        # Iterate over centroid (key, value) pairs to check for counting and speed updates.
        for (objectID, centroid) in centroids.items():
            # Check if a trackable object exists for a centroid.
            trackObj = self.tracks.get(objectID)
            # If there's no existing trackable object for that centroid create a new one.
            if trackObj is None:
                trackObj = TrackableObject.TrackableObject(objectID, centroid, self.frameCount)
                # Add the new trackable object trackObj the dictionary using its id as key.
                self.tracks[objectID] = trackObj
            # If a trackable object exists for the centroid then need to update some things hahaaa.
            else:
                # Compile a list of y-values for the centroid being tracked.
                y = [c[1] for c in trackObj.centroids]
                # Compare the latest y-value for the tracked centroid to the mean of it's y-values.
                # The mean is used to measure the overall direction the item is travelling.
                direction = centroid[1] - np.mean(y)
                # Append the latest position of the centroid to it's tracking data.
                trackObj.centroids.append(centroid)
                # Set the y-value position of the counting line.
                thresh = 250
                # If tracked centroid hasn't been counted then record it's statistics.
                if not trackObj.counted:
                    if direction < 0 and centroid[1] < thresh:
                        self.countUp += 1
                        trackObj.counted = True
                    elif direction > 0 and centroid[1] > thresh:
                        self.countDown += 1
                        trackObj.counted = True

        # Terminate tracks whose centroid has been dismissed.
        for trackID, track in self.tracks.items():
            for ID in self.cenTrack.deregisteredID:
                if track.objectID == ID:
                    track.finished = True
                else:
                    track.currentFrame = self.frameCount

    def process(self):
        global image

        # self.train_subtractor()
        # Initializing a timer that is used to measure if a statistics interval has passed.
        timerStart = datetime.now()
        # # Make sure the node is in the database. *** HANDLED IN MAIN ***
        # db.insert.insert_node(self.id, "Node001", "West", self.longitude, self.latitude)

        """ MAIN LOOP """
        while True and self.frameCount < (self.totalFrames-600):															# Loop will execute until all input processed or user exits.
            # Read a frame of input video.
            _, frame = self.video.read()
            # Apply the subtractor to the frame to get foreground objects.
            mask = self.subtractor.apply(frame)
            # Apply morphology, threshing and median filter.
            mask = self.filter_frame(mask)
            # Get bounding boxes for the foreground objects.
            contours, boundingRect = self.define_contours(mask)
            # Get centroids from the bounding boxes.                *** LOOK INTO WHAT THIS METHOD IS DOING AND IF IT'S NECESSARY ***
            self.cenTrack.update(boundingRect, self.frameCount)
            # Update the object positions and vehicle statistics.   *** MAYBE WANT TO SEPARATE THIS INTO TWO METHODS ***
            self.update_tracks()
            # Convert foreground mask back to a 3-channel image.
            mask = cv.cvtColor(mask, cv.COLOR_GRAY2RGB)
            # Draw graphics onto mask
            self.draw_info(mask, boundingRect)
            # Draw graphics onto original frame
            self.draw_info(frame, boundingRect)
            # Stitch together original image and foreground mask for display.
            combined = np.hstack((frame, mask))
            # Updating the frame shared with Flask app.
            globals.image = frame
            # Increment the number of frames.
            self.frameCount += 1
            # Perform speed measurements                            *** PUT THIS IN A METHOD *** ALSO FIX THE SPEED CALCULATION SO THEY WORK ****
            if self.frameCount % 1 == 0:
                for objID, objs in self.tracks.items():
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
            if (self.frameCount >= (self.totalFrames-600)):
                # Reset frame count.
                self.frameCount = 0
                # Reset video cursor.
                self.video.set(cv.CAP_PROP_POS_FRAMES, 0)

            # Show the result.
            cv.imshow("Combined", combined)

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
