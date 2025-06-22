import cv2
import numpy as np
import sys
from cyndilib.wrapper.ndi_recv import RecvColorFormat, RecvBandwidth
from cyndilib.finder import Finder, Source
from cyndilib.receiver import Receiver, ReceiveFrameType
from cyndilib.video_frame import VideoFrameSync
from cyndilib.audio_frame import AudioFrameSync
from cyndilib.framesync import FrameSyncThread

class NDICam:
    def __init__(self, source_name, verbose=False):
        #adapted from https://github.com/nocarryr/cyndilib/blob/main/examples/viewer.py
        # Create and start a Finder with a callback
        self.source_name = source_name
        self.finder = Finder()
        self.finder.set_change_callback(self.on_finder_change)
        self.finder.open()
        self.ROI = None
        self.verbose = False

        # Create a Receiver without a source
        self.receiver = Receiver(
            color_format=RecvColorFormat.RGBX_RGBA,
            bandwidth=RecvBandwidth.highest,
        )
        self.video_frame = VideoFrameSync()
        self.audio_frame = AudioFrameSync()

        # Add the video/audio frames to the receiver's FrameSync
        self.receiver.frame_sync.set_video_frame(self.video_frame)
        self.receiver.frame_sync.set_audio_frame(self.audio_frame)
        self.ndi_source_names = self.finder.get_source_names()
        if self.source_name is None:
            self.get_first_source()
        self.update_source()
        self.receiver.set_source(self.source)
    
    def capture(self):
        self.receiver.frame_sync.capture_video()
        vf = self.video_frame
        frame = vf.get_array()
        if min(vf.xres, vf.yres) == 0:
            # We haven't received an actual frame yet, do nothing
            return None
        # Convert from buffered rgba to grayscale
        colourDepth = 4
        xRes = frame.shape[0]//(vf.yres*colourDepth)
        newFrame = np.reshape(frame, (vf.yres, xRes, colourDepth))
        grayscale = cv2.cvtColor(newFrame, cv2.COLOR_RGBA2GRAY)[:vf.yres, :vf.xres]
        if self.ROI == None:
            self.ROI = [0, 0, vf.xres, vf.yres]
            return grayscale
        else:
            x, y, w, h = self.ROI
            return grayscale[x:x+w, y:y+h]

    def set_ROI(self, ROI):
        # [x y w h]
        self.ROI = ROI

    def close(self):
        if self.finder is not None:
            self.finder.close()

    def on_finder_change(self):
        if self.finder is None:
            return
        self.ndi_source_names = self.finder.get_source_names()
        self.update_source()

    def update_source(self, *args):
        if self.source_name is None:
            self.source = None
        else:
            with self.finder.notify:
                self.source = self.finder.get_source(self.source_name)
    
    def get_first_source(self):
        if self.source_name is None:
            self.source_name = self.ndi_source_names[0]

if __name__ == "__main__":
    c = NDICam()
    while True:
        vf = c.capture()