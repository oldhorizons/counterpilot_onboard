import platform
plat = platform.platform()
if "windows" in platform.lower():
    plat = "windows"
elif "pi" in platform.lower():
    plat = "pios"
    import picamzero as picam
elif "linux" in platform.lower():
    plat = "linux"
elif "mac" in platform.lower():
    plat = "macos"
import cv2
import numpy as np

class CameraInterface:
    def __init__(self):
        global plat
        match plat:
            case "windows":
                self.cam = cv2.VideoCapture()
            case "pios":
                try:
                    self.cam = picam.Camera()
                except IndexError as error:
                    print("Camera not found. Check your camera's connection")
                    raise IndexError(repr(error))
                self.cam.flip_camera(vflip=True)
            case "linux": 
                pass
            case "macos":
                pass
        self.set_ROI(None)
    
    def capture(self):
        global plat
        match plat:
            case "windows":
                pass
            case "pios":  
                img = self.cam.capture_array()
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                x, y, w, h = self.ROI
                return np.flip(img[y:y+h, x:x+w], 0)
                #return np.flip(img[x:x+w, y:y+h], 0)
                #return img[x+w:x, y+h:y]
            case "linux": 
                pass
            case "macos":
                pass
    
    def set_ROI(self, ROI):
        self.ROI = ROI
        if ROI == "default":
            self.ROI = [2000, 900, 1500, 900] #x, y, w, h - TODO more sensible defaults
        if ROI == None:
            # TODO reset ROI
            pass
    
    def reset(self):
        global plat
        match plat:
            case "windows":
                pass
            case "pios":
                pass
            case "linux": 
                pass
            case "macos":
                pass

    def close(self):
        global plat
        match plat:
            case "windows":
                pass
            case "pios":
                pass
            case "linux": 
                pass
            case "macos":
                pass