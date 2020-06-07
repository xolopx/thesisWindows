from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np


class CentroidTracker:

    def __init__(self, maxDisappeared: object = 25, maxDistance: object = 100, minDistance: object = 30) -> object:
        """
        Stores a list of tracked objects, represented as a centroid coordinate and an associated ID number, in an ordered dictionary.

        :param maxDisappeared: Maximum number of frame a centroid can disappear for before being de-registered.
        :param maxDistance: Maximum distance a centroid can reappear and still be associated with its nearest centroid.
        :param minDistance: Minimum distance a centroid can be to another without getting associated with that centroid.
        """

        # Counter for next unique centroid ID.
        self.nextObjectID = 0
        # Ordered Dictionary of current centroids stored as: {ID, centroid(x,y)}.
        self.centroids = OrderedDict()
        # Dictionary of boxes assigned at the same time as centroids.
        self.boxes = OrderedDict()
        # Ordered Dictionary of IDs for centroids that are not in current frame. Stored as: {ID, missing_frame_count}.
        self.disappeared = OrderedDict()
        # Number of frames a centroid can go missing for before being removed.
        self.maxDisappeared = maxDisappeared
        # The maximum distance a centroid can reappear from it's previous and still be associated.
        self.maxDistance = maxDistance
        # Min distance a centroid can appear near other centroid and not be associated with it.
        self.minDistance = minDistance
        # list of centroid ID numbers that have been dismissed.
        self.deregisteredID = []



    def register(self, centroid):
        """ Registers a new centroid to be tracked.
            :param centroid: Pair (x,y) of a centroid coordinate.
        """
        # Next available unique ID is used for new centroid index in object list.
        self.centroids[self.nextObjectID] = centroid
        # Initially the number of times the centroid has disappeared is 0.
        self.disappeared[self.nextObjectID] = 0
        # Increment the object ID counter.
        self.nextObjectID += 1

    def deregister(self, ID):
        """ Deregisters a centroid with ID objectID.
            :param ID: ID of a centroid.
        """
        # Use ID to get centroid from list of active centroids and delete it.
        del self.centroids[ID]
        # Use ID to get centroid from list of missing centroids and delete it.
        del self.disappeared[ID]

    def update(self, rects):
        """
        Checks bounding box state against centroids state.
        :param rects: List of up-right bounding rectangles.
        :return:

        """

        # Cleanse the records every 1000 centroids.
        if self.nextObjectID > 1000:
            self.nextObjectID = 0


        # If there are no bounding boxes.
        if len(rects) == 0:
            # For all centroid disappeared list IDs.
            for objectID in list(self.disappeared.keys()):
                # Increment each missing centroids frame count.
                self.disappeared[objectID] += 1
                # Check if centroid has passed limit of missing frames.
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)
                    self.deregisteredID.append(objectID)
            # Return the updates list of centroids and deregistered IDs.
            return self.centroids, self.deregisteredID

        # Initialize an array of input centroids for current frame.
        inputCentroids = np.zeros((len(rects), 2), dtype='int')

        # Get centroids for all bounding boxes, and store in an 2D array at index i.
        for (i, (startX, startY, width, height)) in enumerate(rects):
            cX = int((startX + (startX + width)) / 2.0)
            cY = int((startY + (startY + height)) / 2.0)
            inputCentroids[i] = (cX, cY)

        # If there are no active centroids.
        if len(self.centroids) == 0:
            # Register all new centroids.
            for i in range(0, len(inputCentroids)):
                self.register(inputCentroids[i])

        # Else match new centroids with existing ones.
        else:

            objectIDs = list(self.centroids.keys())
            objectCentroids = list(self.centroids.values())
            # Returns distance matrix between old centroids and new centroids.
            D = dist.cdist(np.array(objectCentroids), inputCentroids)
            # Return list of column indices sorted by minimum row values. Smallest to largest.
            cols = D.min(axis = 0).argsort()
            # Returns list of corresponding row indices that pair with the column indices for the smallest values.
            rows = D.argmin(axis = 0)[cols]

            # Tracks which pairs have already been used.
            usedRows = set()
            usedCols = set()

            # Loop over all centroid's minimum distance values.
            for (row, col) in zip(rows, cols):
                # Skip an existing or new centroid if it has already been used.
                if row in usedRows or col in usedCols:
                    continue

                # row (or col) correspond to a centroid's position in the tracked list of centroids.
                objectID = objectIDs[row]

                # If the distance of the nearest centroid is close enough to be assumed to be the centroid.
                if D[row][col] < self.maxDistance:
                    # Set the old centroid's new location to be the its closest friend's location.
                    self.centroids[objectID] = inputCentroids[col]
                    # Reset the centroid's disappeared value as its location has been updated.
                    self.disappeared[objectID] = 0
                else:
                    # If closest centroid is outside threshold mark this tracked one as missing for another frame.
                    self.disappeared[objectID] += 1
                    # Add the new centroid to list of tracked. The pairs are sorted by shortest distance so this
                    # centroid can be added to tracked without fear of using up another tracked centroid's buddy.
                    self.register(inputCentroids[col])

                # Keep track of pairs so that new centroids are used twice.
                usedRows.add(row)
                usedCols.add(col)


            # If there's a mismatch in the number of old and new centroids then some will go unused.
            # Find existing centroids that weren't used.
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            # Find new centroids that weren't used.
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            # There are more old centroids than new ones so for each unused already tracked centroid
            # mark it as missing for another frame.
            if D.shape[0] >= D.shape[1]:
                for row in unusedRows:
                    objectID = objectIDs[row]
                    self.disappeared[objectID] += 1
                    # If the unused centroid was missing for too long, deregister it.;
                    if self.disappeared[objectID] > self.maxDisappeared:
                        self.deregister(objectID)
                        self.deregisteredID.append(objectID)
            # Register all left over new centroids.
            else:
                # combined = []                                           # List of new centroid indices that are genuine new centroids.
                # for col in unusedCols:                                  # Check for unused new centroids
                #     for row in range(D.shape[0]):                       # Check unused centroids against all existing centroids.
                #         if D[row][col] < self.minDistance:              # Check if distance is < minimum.
                #             combined.append(col)                        # Append the index to the list of combined centroids.
                #             # print("Centroid absorbed by {} at {}".format(objectIDs[row], objectCentroids[objectIDs[row]]))
                #
                # for col in unusedCols:
                #     if col not in combined:                             # This centroid has not been absorbed into another.
                #         self.register(inputCentroids[col])
                for col in unusedCols:
                    self.register(inputCentroids[col])


        self.consolidate_centroids()

        return self.centroids, self.deregisteredID                             # Return the set of updated centroids.

    def consolidate_centroids(self):
        """
        Checks distance between all tracked centroids and then merges centroids that are too close together.
        """
        # Extract the key value pairs from the list of centroids.
        centroids = list(self.centroids.values())
        keys = list(self.centroids.keys())
        # List of keys for centroids to be absorbed.
        deregID = []
        # Calculate the distance between centroids.
        D = dist.cdist(centroids, centroids)
        # Get shape of the input centroid matrix.
        dim = np.shape(D)
        # Check if any new centroids are too close together and combine them.
        for row in range(dim[0]):
            for col in range(dim[0]):
                # Check threshold and ignore self to self distance.
                if ((D[row][col] < self.minDistance) and (row != col)):
                    # If either centroids from pair are already consolidated no need to add another.
                    # But if neither already consolidated, deregister column.
                    if keys[row] not in deregID and keys[col] not in deregID:
                        # Add to list of centroids to deregister:
                        deregID.append(keys[col])

        # Deregister the consolidated centroids.
        for key in deregID:
            self.deregister(key)