# import the necessary packages
import numpy as np
import argparse
import imutils
import cv2 as cv


class MotionModel:

    def __init__(self, sensitivity=10):

        # Save frame
        self.frame = None
        self.mask = None
        self.motion = None
        self.contours = None
        self.sensitivity = sensitivity

        # Create the background model
        self.background = cv.createBackgroundSubtractorKNN(history=100)

    # Add the next frame to the motion model
    def nextFrame(self, frame):

        self.frame = frame
        self.getMask(self.frame)
        self.processMask(self.mask)
        self.getContours(self.motion)

    # Get the background mask given a frame, returns mask
    def getMask(self, frame):

        mask = self.background.apply(frame)

        self.mask = mask
        return mask

    def updateSensitivity(self, sensitivity):
        self.sensitivity=sensitivity

    # Process the mask to a motion frame to detect movements, returns motion frame
    def processMask(self, mask):

        # Histogram normalization to avoid sudden light changes
        # binary = cv.cvtColor(src=frame, code=cv.COLOR_BGR2GRAY)
        # binary = cv.equalizeHist(binary)

        # Median blur to reduce salt-and-pepper noise
        motion = cv.medianBlur(mask, 5)

        # Closing operation (erode then dilate) to remove noise
        motion = cv.erode(motion, None, iterations=1)
        motion = cv.dilate(motion, None, iterations=1)

        # Opening operation (dilate then erode) to fill in holes
        motion = cv.dilate(motion, None, iterations=30)
        motion = cv.erode(motion, None, iterations=30)

        self.motion = motion
        return motion

    # Get contours from a motion frame, returns large contours
    def getContours(self, motion):

        cnts = cv.findContours(motion.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # For each contour
        largeCnts = []

        # For each contour
        for c in cnts:

            # if the contour is too small, ignore it
            h, w = motion.shape
            if cv.contourArea(c) < self.sensitivity * w * h / 500:
                continue

            # Else there is motion
            largeCnts.append(c)

        self.contours = largeCnts
        return largeCnts

    # Given a frame, returns true if there is motion
    def isMotion(self):

        # If there is at least one contour, there is motion
        if len(self.contours) > 0:
            return True

        return False

    # Return the bounding boxes
    def boundingBox(self):

        rects = []

        # For each contour, add the bounding box to an array
        for c in self.contours:
            rects.append(cv.boundingRect(c))

        return rects

