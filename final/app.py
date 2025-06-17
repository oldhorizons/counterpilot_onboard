import numpy as np
import cv2
from matplotlib import pyplot as plt
from matplotlib.backend_bases import MouseEvent
from pythonosc import udp_client
from constants import osc_ip, osc_port, verbose, ndi_stream_names, hyperparams
import time
from components.cameras import NDICam
from components import PupilTracker, PupilVisualiser, OscClient

class App:
    def __init__(self):
        global ndi_stream_names
        global osc_ip
        global osc_port
        global hyperparams
        self.cameras = []
        self.networker = OscClient(osc_ip, osc_port)
        for name in ndi_stream_names:
            self.cameras.append(NDICam(name))
        self.tracker = PupilTracker()
        self.visualiser = PupilVisualiser(len(ndi_stream_names))
        self.networker = OscClient()
        self.verbose = verbose

    def start_threaded(self):
        #TODO THIS
        pass

    def first_run(self):
        self.pupilHist = np.zeros(len(self.cameras), 1000, 3)
        # get images from all cameras
        for idx, cam in enumerate(self.cameras):
            img = cam.capture()
        # set all camera ROIs
        #basic set ROI
        if self.tracker.ROI == [0, 0, -1, -1]:
            self.tracker.ROI = self.tracker.get_roi(img)
            print(f"ROI: {self.tracker.ROI}")


    def run(self):
        self.first_run()
        while(True):
            for idx, cam in enumerate(self.cameras):
                img = cam.capture()
                pupil = self.tracker.detect_pupil_agreement(img)
                if pupil != None:
                    x, y, d = self.tracker.normalise_pupil(pupil)
                    #send off
                    self.networker.send_pupil(idx, x, y, d)
    
    def run(self):
        first_run = True
        while(True):
            img = self.collect_image()
            pupil = self.tracker.track_pupil(img)
            if pupil == None:
                print("Pupil invalid.")
                continue
            if self.debug or first_run:
                first_run = False
                self.draw_pupil_and_show(img, pupil)
            

if __name__ == "__main__":
    tracker = PupilTracker(osc_ip, osc_port)
    tracker.run_verbose()
