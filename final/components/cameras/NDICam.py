import cv2
import numpy as np
import sys
import NDIlib as ndi

from constants import ndi_stream_name

class NDICam(CameraInterface):
    def __init__(self):
        if not ndi.initialize():
            raise Exception("Failed to initialise NDI.")
        
        ndi_find = ndi.find_create_v2()
        if ndi_find is None:
            raise Exception("No NDI sources found.")

        sources = []
        while not len(sources) > 0:
            print('Looking for sources ...')
            ndi.find_wait_for_sources(ndi_find, 1000)
            sources = ndi.find_get_current_sources(ndi_find)

        ndi_recv_create = ndi.RecvCreateV3()
        ndi_recv_create.color_format = ndi.RECV_COLOR_FORMAT_BGRX_BGRA

        self.recv = ndi.recv_create_v3(ndi_recv_create)

        if self.recv is None:
            return 0

        ndi.recv_connect(self.recv, sources[0])

        ndi.find_destroy(ndi_find)

    
    def capture(self):
        t, v, a, _ = ndi.recv_capture_v2(self.recv, 1000)

        if t == ndi.FRAME_TYPE_NONE:
            print('No data received.')
            return None

        if t == ndi.FRAME_TYPE_VIDEO:
            print('Video data received (%dx%d).' % (v.xres, v.yres))
            if self.ROI is not None:
                return v.data
            else:
                x, y, w, h = self.ROI
                return v.data[x, x+w, y, y+h]
            ndi.recv_free_video_v2(self.recv, v)

        if t == ndi.FRAME_TYPE_AUDIO:
            print('Audio data received (%d samples).' % a.no_samples)
            ndi.recv_free_audio_v2(self.recv, a)

    
    def set_ROI(self, ROI):
        # [x y w h]
        self.ROI = ROI

    def close(self):
        ndi.recv_destroy(self.recv)
        ndi.destroy()


