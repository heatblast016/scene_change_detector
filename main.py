import asyncio
import os
from datetime import datetime

import cv2 as cv

# Get camera
from MotionDetection import MotionModel
from UserParams import UserParams
from MotionRecording import MotionRecording
from UserInterface import UserInterface


paramPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def drawTimeStamp(frame, width, height):
    currentTime = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    cv.putText(frame, currentTime, (int(width) - 190, int(height) - 10),
               cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)


async def main():
    # getting pre-stored parameters from file, or initializing by default
    settings = UserParams(5, 300, 30, True, False)

    savePath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if os.path.isfile(savePath + "/settings.txt"):
        settings.importParams(savePath + "/settings.txt")
    else:
        settings.exportParams(paramPath+"/settings.txt")

    settings.printParams()
    motionLimit, sensitivity, camFPS, record, drawBoxes = settings.getParams()
    model = MotionModel(sensitivity)

    # internal function for updating and serializing parameters
    def updateParams(lim, sense, fps, rec, dB):
        nonlocal settings, motionLimit, sensitivity, camFPS, record, drawBoxes, model, recording
        settings = UserParams(lim, sense, fps, rec, dB)
        settings.exportParams(paramPath+"/settings.txt")
        motionLimit = lim
        sensitivity = sense
        camFPS = fps
        record = rec
        drawBoxes = dB

        model.updateSensitivity(sensitivity)

        if recording.currentlyRecording and  recording.record:
            savePath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                    '..')) + "/VideoRecordings/"
            os.makedirs(savePath, exist_ok=True)
            print(savePath)
            asyncio.create_task(
                recording.b.export(outPath=savePath + datetime.now().strftime("%d_%m_%Y %H_%M_%S") + ".avi",
                                   fps=recording.camFPS))

            recording.currentlyRecording = False;

            recording = MotionRecording(capture.get(3), capture.get(4),
                                        motionLimit, camFPS, record)

        else:
            recording.updateSettings(motionLimit, camFPS, record)

    # initialize camera to first camera available
    camera = 0
    capture = None
    for cam in range(-1, 10):
        capture = cv.VideoCapture(cam)
        if capture.isOpened():
            settings = UserParams(motionLimit, sensitivity, camFPS,
                                  record, drawBoxes)
            settings.exportParams(paramPath+"/settings.txt")
            camera = cam
            break
        capture.release()

    # iterate camera upward or downward until another open stream is found
    def updateCamera(increment):
        nonlocal camera, capture

        if increment == 1:
            # increment camera in positive direction
            for c in range(camera+1, 10):
                newCapture = cv.VideoCapture(c)
                if newCapture.isOpened():
                    capture = newCapture
                    camera = c

                    return
                newCapture.release()

            for c in range(-1, camera):
                newCapture = cv.VideoCapture(c)
                if newCapture.isOpened():
                    capture = newCapture
                    camera = c

                    return
                newCapture.release()
        else:
            # increment camera in negative direction
            for c in range(camera-1, -2, -1):
                newCapture = cv.VideoCapture(c)
                if newCapture.isOpened():
                    capture = newCapture
                    camera = c

                    return
                newCapture.release()

            for c in range(10, camera, -1):
                newCapture = cv.VideoCapture(c)
                if newCapture.isOpened():
                    capture = newCapture
                    camera = c

                    return
                newCapture.release()

    # initialize recording and UI
    recording = MotionRecording(capture.get(3), capture.get(4), motionLimit, camFPS, record)
    UI = UserInterface(capture.get(3), capture.get(4), updateParams, updateCamera, settings, drawBoxes, savePath, camera)

    while True:
        ret, frame = capture.read()  # read the frame from camera feed

        # use per-frame algorithm for each part of the program (motion detection, UI, recording)
        drawTimeStamp(frame, capture.get(3), capture.get(4))
        model.nextFrame(frame)
        recording.nextFrame(frame, model.isMotion())
        UI.streamUpdate(frame.copy(), model.boundingBox(), model.isMotion())
        UI.videoUpdate()

        await asyncio.sleep(0)


mainTask = asyncio.run(main())
