import matplotlib.pyplot as plt
import cv2
from matplotlib.widgets import RectangleSelector

colours = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255,255,255)]

class PupilVisualiser:
    def __init__(self, verbose=False, nCams=1):
        self.graph = None
        self.verbose = verbose
        self.nCams = nCams
        
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

    def draw_pupil_and_show(self, cv2Image, pupil):
        if pupil==None:
            return
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
        global colours
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
            try:
                cv2.ellipse(colourImg, (x, y), (dMin//2, dMaj//2), angle, 0, 360, colours[i], 2)
            except:
                continue
        #cv2.imwrite(f"images/{time.time()}.jpg", colourImg)
        print(confidences)
        confidences = ["no  ", "pupils"]
        if self.graph == None:
            self.init_graph(colourImg, ','.join(confidences))
        else:
            self.update_graph(colourImg, ','.join(confidences))

    def init_graph_multicam(self, cv2Image, title, index):
        pass

    def update_graph_multicam(self, cv2Image, title, index):
        pass

    
    
    def get_eye_roi_manual(self, cv2Image):
        fig = plt.figure(layout='constrained')
        ax = fig.subplots()
        ax.set_title("Click and drag to select ROI")
        s = RectangleSelector(ax, onselect=self.select_callback)
        ax.imshow(cv2Image)
        input("Confirm ROI?")
        roi = self.selectROI
        self.selectROI = []
        return roi
        
    def select_callback(self, eclick, erelease):
        #https://matplotlib.org/stable/gallery/widgets/rectangle_selector.html
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        print(f"{x1} {x2} {y1} {y2}")
        x = min(x1, x2)
        w = max(x1, x2) - x
        y = min(y1, y2)
        h = max(y1, y2) - y
        self.selectROI = [x, y, w, h]