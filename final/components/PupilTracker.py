import numpy as np
import cv2
import pypupilext as pp
from matplotlib import pyplot as plt
from matplotlib.backend_bases import MouseEvent
from constants import hyperparams
import time

colours = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255,255,255)]

class PupilTracker:
    def __init__(self, verbose):
        self.find_face = True #if face first needs to be identified.
        self.model = pp.PuReST()
        self.models = [pp.ElSe(), pp.ExCuSe(), pp.PuRe(), pp.PuReST(), pp.Starburst(), pp.Swirski2D()]
        self.eye_finder = cv2.CascadeClassifier('data/haarcascades/haarcascade_eye.xml')
        self.face_finder = cv2.CascadeClassifier('data/haarcascades/haarcascade_frontalface_default.xml')

    def detect_eye(self, cv2Image):
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
        xEye += xFace
        yEye += yFace
        return (xEye, yEye, wEye, hEye)
    
    def extract_pupil_attrs(self, pupil):
        x, y = pupil.center
        d = pupil.majorAxis()
        x = int(x)
        y = int(y)
        d = int(d)
        return x, y, d
    
    def detect_pupil(self, cv2Image, model):
        if model == None:
            model = self.model
        pupil = model.run(cv2Image)
        return pupil
    
    def detect_pupil_agreement(self, cv2Image, prev_d):
        global hyperparams, colours
        if prev_d != None:
            diam_min_px = prev_d + hyperparams["deltaD_tolerance"]*prev_d
            diam_max_px = prev_d - hyperparams["deltaD_tolerance"]*prev_d

        pupils = [model.run(cv2Image) for model in self.models]
        # if pupil is outside appropriate size range, discard
        for i in range(len(pupils)-1, -1, -1):
            if pupils[i] == None or pupils[i].confidence < hyperparams["confidence_threshold"]:
                pupils.pop(i)
            s = pupils[i].size
            if prev_d != None and (s[0] < diam_min_px or  s[1] < diam_min_px or s[0] > diam_max_px or s[1] > diam_max_px):
                pupils.pop(i)
        # calculate  centers of  new pupil collection
        median_center = np.median(np.array([pupil.center for pupil in pupils]))
        # remove all pupils with center outside range tolerance
        for i in range(len(pupils)-1, -1, -1):
            d = np.linalg.norm(median_center - pupils[i].center)
            if d > hyperparams["centerDiff_tolerance"]:
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