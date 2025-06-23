import numpy as np
import cv2
import pypupilext as pp
from appConstants import hyperparams
import numpy as np

class PupilTracker:
    def __init__(self, verbose=False):
        self.model = pp.PuReST()
        self.models = [pp.ElSe(), pp.ExCuSe(), pp.PuRe(), pp.PuReST(), pp.Starburst(), pp.Swirski2D()]
        self.eye_finder = cv2.CascadeClassifier('modeldata/haarcascades/haarcascade_eye.xml')
        self.face_finder = cv2.CascadeClassifier('modeldata/haarcascades/haarcascade_frontalface_default.xml')
        self.verbose = verbose
        self.rois = dict()
        self.pupilHistory = dict()

    def get_eye_roi(self, cv2Image):
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
        return [xEye, yEye, wEye, hEye]
    
    def extract_pupil_attrs(self, pupil):
        x, y = pupil.center
        d = pupil.majorAxis()
        x = int(x)
        y = int(y)
        d = int(d)
        return x, y, d
    
    def detect_pupil(self, cv2Image, model=None, pupilId = None,):
        if model == None:
            model = self.model
        pupil = model.run(cv2Image)
        return pupil
    
    def detect_pupil_agreement(self, cv2Image, pupilId = None):
        global hyperparams, colours
        if pupilId not in self.pupilHistory.keys():
            self.pupilHistory[pupilId] = []
            prev_d = None
        else:
            prev_d = self.pupilHistory[pupilId].majorAxis()
            diam_min_px = prev_d + hyperparams["deltaD_tolerance"]*prev_d
            diam_max_px = prev_d - hyperparams["deltaD_tolerance"]*prev_d


        pupils = [model.run(cv2Image) for model in self.models]
        # if pupil is outside appropriate size range, discard
        priorities = [0 for i in range(len(pupils))]
        if prev_d != None:
            pass
            # priorities = [p.confidence*(np.mean(p.size)) for p in pupils]
        for i in range(len(pupils)-1, -1, -1):
            if pupils[i] == None or pupils[i].confidence < hyperparams["confidence_threshold"]:
                #discard pupils that don't meet confidence threshold
                priorities[i] -= 2
            else:
                s = pupils[i].size
                if prev_d != None and (s[0] < diam_min_px or  s[1] < diam_min_px or s[0] > diam_max_px or s[1] > diam_max_px):
                    priorities[i] -= 1
        # calculate  centers of  new pupil collection
        median_center = np.median(np.array([pupil.center for pupil in pupils]))
        # remove all pupils with center outside range tolerance
        for i in range(len(pupils)-1, -1, -1):
            d = np.linalg.norm(median_center - pupils[i].center)
            if d > hyperparams["centerDiff_tolerance"]*cv2Image.shape[0]:
                priorities[i] -= 0.5
        # give priority to pupil with smallest ellipse within tolerances
        priorities[pupils.index(min(pupils, key=lambda pupil:max(pupil.size)))] += 2
        return pupils[priorities.index(max(priorities))]
    
    def get_all_pupils(self, cv2Image):
        return [model.run(cv2Image) for model in self.models]

    def track(self, img):
        pupils = []
        for model in self.models:
            pupils.append(model.runWithConfidence(img))
        pupil = self.track_pupil_agreement(img)
        pupils.append(pupil)
        return pupils
    
