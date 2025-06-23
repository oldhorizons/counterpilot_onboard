import matplotlib.pyplot as plt
import cv2
import math
from matplotlib.widgets import RectangleSelector

colours = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255,255,255)]
# pp.ElSe(), pp.ExCuSe(), pp.PuRe(), pp.PuReST(), pp.Starburst(), pp.Swirski2D()
# ElSe:red, ExCuSe:green, PuRe:blue, PuReST:yellow, Starburst:magenta, Swirski2D:cyan, final:white

class PupilVisualiser:
    def __init__(self, verbose=False, nCams=1):
        self.axs = None
        self.graph = None
        self.verbose = verbose
        self.nCams = nCams
        self.ROIUpdateAvailable = False
        self.ROIs = []
        self.IdMap = dict()
        
    def init_graph_multi(self, cv2Images, nCams=1):
        plt.ion()
        nCols = math.floor(math.sqrt(nCams))
        nRows = math.ceil(nCams/nCols)
        for i in range(nCams):
            colNum = i//nCols
            rowNum = i%nCols
            self.IdMap[i] = [colNum, rowNum]
        self.axs, self.figs = plt.subplots(ncols=nCols, nrows=nRows)
        self.axs.axes[0].imshow(cv2Images)
        for i, img in enumerate(cv2Images):
            c, r = self.IdMap[i]
            self.axs.axes[i].imshow(img)
        self.selector = RectangleSelector(self.axs, onselect=self.select_callback)
        plt.show()
        plt.pause(0.005)
    
    def init_graph_single(self, cv2Image):
        plt.ion()
        self.graph = plt.imshow(cv2Image)
        # self.selector = RectangleSelector(self.axs, onselect=self.select_callback)
        plt.show()
        plt.pause(0.005)
    
    def update_image(self, cv2Image, id):
        try:
            c, r = self.IdMap[id]
            self.axs.axes[id].remove()
            self.axs.axes[id].imshow(cv2Image)
            self.axs.draw()
        except:
            return
        plt.pause(0.005)
        
    def update_graph_single(self, cv2Image):
        self.graph.remove()
        self.graph = plt.imshow(cv2Image)
        self.graph.draw()
        plt.pause(0.005)

    def update_graph_multi(self, cv2Images):
        for i, img in enumerate(cv2Images):
            self.update_image(img, i)
        plt.pause(0.005)

    def draw_pupil_single(self, cv2Image, pupil):
        cv2Image = self.get_pupil(cv2Image, pupil)
        if self.axs == None:
            self.init_graph_single(cv2Image)
        else:
            self.update_graph_single(cv2Image)

    def draw_all_pupils_single(self, cv2Image, pupils):
        cv2Image = self.get_all_pupils(cv2Image, pupils)
        if self.axs == None:
            self.init_graph_single(cv2Image)
        else:
            self.update_graph_single(cv2Image)

    def draw_pupil_multicam(self, cv2Images, pupils):
        for i, img in enumerate(cv2Images):
            pupil = pupils[i]
            cv2Images[i] = self.get_pupil(img, pupil)
        if self.axs == None:
            self.init_graph_multi(cv2Images, nCams = len(cv2Images))
        else:
            self.update_graph_multi(cv2Images)

    def draw_all_pupils_multicam(self, cv2Images, pupils):
        for i, img in enumerate(cv2Images):
            pupilae = pupils[i]
            cv2Images[i] = self.get_all_pupils(img, pupilae)
        if self.axs == None:
            self.init_graph_multi(cv2Images, nCams = len(cv2Images))
        else:
            self.update_graph_multi(cv2Images)
    
    def get_pupil(self, cv2Image, pupil):
        if pupil==None:
            return
        else:
            x, y = pupil.center
            x = int(x)
            y  = int(y)
            dMaj = int(pupil.majorAxis())
            dMin = int(pupil.minorAxis())
            angle = pupil.angle
        colourImg = cv2.cvtColor(cv2Image, cv2.COLOR_GRAY2RGB)
        return cv2.ellipse(colourImg, (x, y), (dMin//2, dMaj//2), angle, 0, 360, (255, 0, 255), 2)
        
    def get_all_pupils(self, cv2Image, pupils):
        colourImg = cv2.cvtColor(cv2Image, cv2.COLOR_GRAY2RGB)
        global colours
        # pp.ElSe(), pp.ExCuSe(), pp.PuRe(), pp.PuReST(), pp.Starburst(), pp.Swirski2D()
        # ElSe:red, ExCuSe:green, PuRe:blue, PuReST:yellow, Starburst:magenta, Swirski2D:cyan, final:white
        for i, pupil in enumerate(pupils):
            if pupil==None:
                continue
            x, y = pupil.center
            x = int(x)
            y  = int(y)
            dMaj = int(pupil.majorAxis())
            dMin = int(pupil.minorAxis())
            angle = pupil.angle
            try:
                cv2.ellipse(colourImg, (x, y), (dMin//2, dMaj//2), angle, 0, 360, colours[i], 2)
            except:
                continue
        return colourImg
        
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