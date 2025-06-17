import picamzero as picam
import numpy as np
import cv2
import pypupilext as pp
from matplotlib import pyplot as plt
from matplotlib.backend_bases import MouseEvent
from pythonosc import udp_client
from constants import osc_ip, osc_port, debug, roi_size
import time
from components.cameras import NDICam
from components import PupilTracker, PupilVisualiser, OscCilent

class App:
    def __init__(self, osc_ip, osc_port):
        self.cam = CameraInterface()
        self.tracker = PupilTracker()
        self.visualiser = Visualiser()
        self.networker = OscClient()
        self.verbose

    def run(self):
        first_run = True
        while(True):
            t0 = time.time()
            img = self.cam.capture()
            if self.verbose:
                cv2.imwrite(f"images/undrawn/{time.time()}.jpg", img)
                t1 = time.time()
                print(f"image collected in {t1  - t0} seconds")
                t2 = time.time()
                print(f"pupil identified in {t2 - t1} seconds")
            pupils = self.tracker.track(img)
            if self.verbose and (self.debug or first_run):
                self.draw_all_pupils_and_show(img, pupils)
                t3  = time.time()
                print(f"pupil drawn in {t3 - t2} seconds")
            #basic set ROI
            if self.tracker.ROI == [0, 0, -1, -1]:
                self.tracker.ROI = self.tracker.get_roi(img)
                print(f"ROI: {self.tracker.ROI}")
            #x, y, d = self.normalise_pupil(pupil)
            t4 = time.time()
            print(f"pupil normalised in {t3 - t4} seconds")
            #send off
            #self.send_pupil(x, y, d)
            t5 = time.time()
            print(f"pupil sent in {t4 - t5} seconds")
            print(f"TOTAL TIME: {t5 - t0} seconds")
            time.sleep(0.01)
    
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
