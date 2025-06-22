import picamzero as picam
import cv2
import numpy as np

class PiCam(CameraInterface):
    def __init__(self):
        try:
            self.cam = picam.Camera()
        except IndexError as error:
            print("Camera not found. Check your camera's connection")
            raise IndexError(repr(error))
        self.cam.flip_camera(vflip=True)
        self.set_ROI(None)
    
    def capture(self):
        img = self.cam.capture_array()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        x, y, w, h = self.ROI
        return np.flip(img[y:y+h, x:x+w], 0)
        #return np.flip(img[x:x+w, y:y+h], 0)
        #return img[x+w:x, y+h:y]
    
    def set_ROI(self, ROI):
        self.ROI = ROI
        if ROI == "default":
            self.ROI = [2000, 900, 1500, 900] #x, y, w, h - TODO more sensible defaults
        if ROI == None:
            # TODO reset ROI
            pass

    def close(self):
        self.cam.release()