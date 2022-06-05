# File imports
import cv2 as cv
import queue
import asyncio


class Buffer:

    def __init__(self, outType, height, width):
        self.size = (width, height)
        self.outType = outType
        self.buffer = queue.Queue()


    def update(self, frame):

        self.buffer.put(frame)
        self.buffer.get()
    # add a frame to the buffer, then remove one from the front

    def append(self, frame):

        self.buffer.put(frame)

    # add a frame to the buffer

    async def export(self, outPath, fps):

        # export video from Buffer to given output path
        print("start exporting")

        output = cv.VideoWriter(outPath, cv.VideoWriter_fourcc(*self.outType), fps, self.size)

        while not self.buffer.empty():
            output.write(self.buffer.get())
            await asyncio.sleep(0)

        print("finish exporting")

        output.release()


