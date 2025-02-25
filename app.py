import picamzero as picam
import numpy as np
import cv2
import pypupilext as pp
from matplotlib import pyplot as plt
from matplotlib.backend_bases import MouseEvent
from pythonosc import udp_client
from constants import osc_ip, osc_port, debug, roi_size
import time

diam_min_px = 20
diam_max_px = 500
diam_min_mm = 2.0
diam_max_mm = 8.0
center_tolerance_px = 200

class PupilTracker:
    def __init__(self, osc_ip, osc_port):
        global debug
        self.debug = debug
        self.model = pp.PuReST()
        if self.debug:
            self.models = [pp.ElSe(), pp.ExCuSe(), pp.PuRe(), pp.PuReST(), pp.Starburst(), pp.Swirski2D()]
        try:
            self.cam = picam.Camera()
        except IndexError as error:
            print("Camera not found. Check your camera's connection")
            raise IndexError(repr(error))
        self.cam.flip_camera(vflip=True)
        self.eye_finder = cv2.CascadeClassifier('data/haarcascades/haarcascade_eye.xml')
        self.face_finder = cv2.CascadeClassifier('data/haarcascades/haarcascade_frontalface_default.xml')
        self.ROI = [2000, 900, 1500, 900] #x, y, w, h
        self.roi_center = None
        self.pupilID = 1
        self.dhist = []
        self.graph = None
        self.oscClient = udp_client.SimpleUDPClient(osc_ip, osc_port)
        print(f"Initialised OSC client to {osc_ip}:{osc_port}")
    
    def send_pupil(self, x, y, d):
        id = self.pupilID
        self.oscClient.send_message(f"/cue/eye{id}D/name", d)
        self.oscClient.send_message(f"/cue/eye{id}X/name", x)
        self.oscClient.send_message(f"/cue/eye{id}Y/name", y)
        print(f"sent d{d}x{x}y{y}")
        
    def init_graph(self, cv2Image, title):
        plt.ion()
        self.graph = plt.imshow(cv2Image)
        plt.title(f"Confidence: {title}")
        plt.show()
        # plt.pause(0.005)

    def update_graph(self, cv2Image, title):
        self.graph.remove()
        self.graph = plt.imshow(cv2Image)
        plt.title(f"Confidence: {title}")
        plt.draw()
        plt.pause(0.005)
    
    def get_roi(self, cv2Image):
        #todo detect face
        eyes = self.eye_finder.detectMultiScale(cv2Image, 1.3, 5)
        if len(eyes) == 0:
            print("didn't find an eye")
            return (0, 0, -1, -1)
        maxEye = eyes[np.argmax(eyes, 0)].tolist()[0] 
        x, y, w, h  = maxEye
        return (x, y, w, h)

    def draw_pupil_and_show(self, cv2Image, pupil):
        if pupil==None:
            x, y, dMaj, dMin, angle, confidence = 10, 10, 50, 20, 80, 0.5
        else:
            x, y = pupil.center
            x = int(x)
            y  = int(y)
            dMaj = int(pupil.majorAxis())
            dMin = int(pupil.minorAxis())
            angle = pupil.angle
            confidence = pupil.confidence
        colourImg = cv2.cvtColor(cv2Image, cv2.COLOR_GRAY2RGB)
        cv2.ellipse(colourImg, (x, y), (dMin//2, dMaj//2), angle, 0, 360, (255, 0, 255), 2)
        if self.graph == None:
            self.init_graph(colourImg, confidence)
        else:
            self.update_graph(colourImg, confidence)
        
    def draw_all_pupils_and_show(self, cv2Image, pupils):
        colourImg = cv2.cvtColor(cv2Image, cv2.COLOR_GRAY2RGB)
        colours = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255,255,255)]
        confidences = []
        # pp.ElSe(), pp.ExCuSe(), pp.PuRe(), pp.PuReST(), pp.Starburst(), pp.Swirski2D()
        # ElSe:red, ExCuSe:green, PuRe:blue, PuReST:yellow, Starburst:magenta, Swirski2D:cyan, final:white
        for i, pupil in enumerate(pupils):
            if pupil==None:
                confidences.append(0)
                continue
            x, y = pupil.center
            x = int(x)
            y  = int(y)
            dMaj = int(pupil.majorAxis())
            dMin = int(pupil.minorAxis())
            angle = pupil.angle
            confidences.append(str(int(100*pupil.confidence)))
            cv2.ellipse(colourImg, (x, y), (dMin//2, dMaj//2), angle, 0, 360, colours[i], 2)
        cv2.imwrite(f"images/{time.time()}.jpg", colourImg)
        if self.graph == None:
            self.init_graph(colourImg, ','.join(confidences))
        else:
            self.update_graph(colourImg, ','.join(confidences))
    
    def collect_image(self):
        img = self.cam.capture_array()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        x, y, w, h = self.ROI
        return np.flip(img[y:y+h, x:x+w], 0)
        #return np.flip(img[x:x+w, y:y+h], 0)
        #return img[x+w:x, y+h:y]
    
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
        global diam_min_px, diam_max_px, center_tolerance_px
        pupils = [model.run(cv2Image) for model in self.models]
        discards = []
        # if pupil is outside appropriate size range, discard
        for i in range(len(pupils)-1, -1, -1):
            if pupils[i] == None:
                pupils.pop(i)
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
    
    def run_verbose(self):
        first_run = True
        while(True):
            t0 = time.time()
            img = self.collect_image()
            t1 = time.time()
            print(f"image collected in {t1  - t0} seconds")
            pupils = []
            for model in self.models:
                pupils.append(model.runWithConfidence(img))
            pupil = self.track_pupil_agreement(img)
            pupils.append(pupil)
            t2 = time.time()
            print(f"pupil identified in {t2 - t1} seconds")
            if pupil == None:
                print("Pupil invalid.")
                continue
            if self.debug or first_run:
                self.draw_all_pupils_and_show(img, pupils)
                #self.draw_pupil_and_show(img, pupil)
                t3  = time.time()
                print(f"pupil drawn in {t3 - t2} seconds")
            #basic set ROI
            if self.ROI == [0, 0, -1, -1]:
                self.ROI = self.get_roi(img)
                print(f"ROI: {self.ROI}")
            #x, y, d = self.normalise_pupil(pupil)
            t4 = time.time()
            print(f"pupil normalised in {t3 - t4} seconds")
            #send off
            #self.send_pupil(x, y, d)
            t5 = time.time()
            print(f"pupil sent in {t4 - t5} seconds")
            print(f"TOTAL TIME: {t5 - t0} seconds")
            time.sleep(0.01)
        self.cam.release()
    
    def run(self):
        first_run = True
        while(True):
            img = self.collect_image()
            pupil = self.track_pupil(img)
            if pupil == None:
                print("Pupil invalid.")
                continue
            if self.debug or first_run:
                self.draw_pupil_and_show(img, pupil)
            

if __name__ == "__main__":
    tracker = PupilTracker(osc_ip, osc_port)
    tracker.run_verbose()
