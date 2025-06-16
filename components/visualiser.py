import matplotlib.pyplot as plt
import cv2

class PupilVisualiser:
    def __init__(self):
        self.graph = None
        
    def init_graph(self, cv2Image, title):
        plt.ion()
        self.graph = plt.imshow(cv2Image)
        plt.title(f"Confidence: {title}")
        plt.show()
        # plt.pause(0.005)
    
    def update(self, cv2Image, title):
        self.graph.remove()
        self.graph = plt.imshow(cv2Image)
        plt.title(f"Confidence: {title}")
        plt.draw()
        plt.pause(0.005)

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
            cv2.ellipse(colourImg, (x, y), (dMin//2, dMaj//2), angle, 0, 360, colours[i], 2)
        #cv2.imwrite(f"images/{time.time()}.jpg", colourImg)
        print(confidences)
        confidences = ["no  ", "pupils"]
        if self.graph == None:
            self.init_graph(colourImg, ','.join(confidences))
        else:
            self.update_graph(colourImg, ','.join(confidences))
    
    
