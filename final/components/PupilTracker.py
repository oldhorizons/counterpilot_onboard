import numpy as np
import cv2
import pypupilext as pp
from matplotlib import pyplot as plt
from matplotlib.backend_bases import MouseEvent
from constants import debug, roi_size
import time
from components import CameraInterface
from components import PupilTracker, PupilVisualiser

diam_min_px = 20
diam_max_px = 500
diam_min_mm = 2.0
diam_max_mm = 8.0
center_tolerance_px = 200
colours = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255,255,255)]

class PupilTracker:
    def __init__(self):
        global debug
        self.debug = debug
        self.find_face = True #if face first needs to be identified.
        self.model = pp.PuReST()
        self.models = [pp.ElSe(), pp.ExCuSe(), pp.PuRe(), pp.PuReST(), pp.Starburst(), pp.Swirski2D()]
        self.eye_finder = cv2.CascadeClassifier('data/haarcascades/haarcascade_eye.xml')
        self.face_finder = cv2.CascadeClassifier('data/haarcascades/haarcascade_frontalface_default.xml')
        self.ROI = [2000, 900, 1500, 900] #x, y, w, h
        self.roi_center = None
        self.pupilID = 1
        self.dhist = []
        self.graph = None

    def get_roi(self, cv2Image):
        if self.find_face:
            faces = self.face_finder.detectMultiScale(cv2Image, 1.3, 5)
            if len(faces) == 0:
                xFace, yFace = 0,0
            else:
                xFace, yFace, wFace, hFace = faces[np.argmax(faces, 0)[2]].tolist() #get biggest detected face, measured by width
                cv2Image = cv2Image[yFace:yFace+hFace, xFace:xFace+wFace]
        eyes = self.eye_finder.detectMultiScale(cv2Image, 1.3, 5)
        if len(eyes) == 0:
            print("didn't find an eye")
            return (0, 0, -1, -1)
        maxEye = eyes[np.argmax(eyes, 0)].tolist()[0] 
        xEye, yEye, wEye, hEye  = maxEye
        if self.find_face:
            xEye += xFace
            yEye += yFace
        return (xEye, yEye, wEye, hEye)
    
    def normalise_pupil(self, pupil):
        x, y = pupil.center
        d = pupil.majorAxis()
        x = int(x)
        y = int(y)
        d = int(d)
        #todo Normalise - convert to likely mm, smooth outliers, 
        return x, y, d
        
    def track_pupil(self, cv2Image):
        #use model
        pupil = self.model.run(cv2Image)
        return pupil
        #detect outliers
        pass
        return None
    
    def track_pupil_agreement(self, cv2Image):
        global diam_min_px, diam_max_px, center_tolerance_px, colours
        pupils = [model.run(cv2Image) for model in self.models]
        discards = []
        # if pupil is outside appropriate size range, discard
        for i in range(len(pupils)-1, -1, -1):
            if pupils[i] == None:
                pupils.pop(i)
                colours[i] = (80, 80, 80)
            s = pupils[i].size
            #s = (pupils[i].majorAxis(), pupils[i].minorAxis())
            if s[0] < diam_min_px or  s[1] < diam_min_px or s[0] > diam_max_px or s[1] > diam_max_px:
                pupils.pop(i)
        # calculate  centers of  new pupil collection
        median_center = np.median(np.array([pupil.center for pupil in pupils]))
        # remove all pupils with center outside range tolerance
        for i in range(len(pupils)-1, -1, -1):
            d = np.linalg.norm(median_center - pupils[i].center)
            if d > center_tolerance_px:
                pupils.pop(i)
        # return pupil with smallest ellipse within tolerances
        if len(pupils) == 0:
            return None
        return min(pupils, key=lambda pupil:max(pupil.size))
        
        # pp.ElSe(), pp.ExCuSe(), pp.PuRe(), pp.PuReST(), pp.Starburst(), pp.Swirski2D()
        # ElSe:red, ExCuSe:green, PuRe:blue, PuReST:yellow, Starburst:magenta, Swirski2D:cyan, final:white
    
    def track(self, img):
        pupils = []
        for model in self.models:
            pupils.append(model.runWithConfidence(img))
        pupil = self.track_pupil_agreement(img)
        pupils.append(pupil)
        return pupils