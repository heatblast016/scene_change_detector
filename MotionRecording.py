# import the necessary packages
import asyncio
from _datetime import datetime
import time
import os

from Buffer import Buffer


class MotionRecording:

    def __init__(self, width, height, motionLimit, camFPS, record):

        self.width = width
        self.height = height
        self.isMotion = False
        self.motionLimit = motionLimit
        self.camFPS = camFPS
        self.record = record

        # Get motion model and buffer
        self.b = Buffer(outType="XVID", width=int(self.width),
                        height=int(self.height))

        # Save current time, not currently recording
        self.lastMotion = time.perf_counter()
        self.currentlyRecording = False

    def updateSettings(self, motionLimit, camFPS, record):
        self.motionLimit = motionLimit
        self.camFPS = camFPS
        self.record = record

    # Next frame
    def nextFrame(self, frame, isMotion):

        # If moving, update lastMotion time
        if isMotion and self.record:
            self.lastMotion = time.perf_counter()
            if not self.currentlyRecording:
                self.currentlyRecording = True
                print("start recording")

        # Apply the frame to the buffer
        exported = self.bufferAction(frame)

        # If the previous frame is being exported, create a new buffer
        if exported:
            self.b = Buffer(outType="XVID", width=int(self.width), height=int(self.height))

    # Applies a new frame to buffer
    def bufferAction(self, frame):
        # If recording and there is motion
        if self.record and self.currentlyRecording:

            # And limit is reached, start exporting video
            if time.perf_counter() - self.lastMotion >= self.motionLimit:

                savePath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) + "/VideoRecordings/"
                os.makedirs(savePath, exist_ok=True)
                asyncio.create_task(
                    self.b.export(outPath=savePath + datetime.now().strftime("%d_%m_%Y %H_%M_%S") + ".avi",
                                  fps=self.camFPS))

                self.currentlyRecording = False
                print("stop recording")

                # Return true for exported
                return True

            # If limit isn't reached, keep adding frames to buffer
            else:
                self.b.append(frame)

        # If not recording or no motion, simply update the buffer
        else:
            if self.b.buffer.qsize() >= self.camFPS * self.motionLimit:
                self.b.update(frame)
            else:
                self.b.append(frame)

        return False
