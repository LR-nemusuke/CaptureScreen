import pyautogui as pag
import numpy as np
import time
import cv2
import PySimpleGUI as sg
import os
import glob
from datetime import datetime

# initialize default parameter
# -------------------------------------------
screenImage = pag.screenshot()
screenImage.save("screen.png")
img_height, img_width = pag.size()
screen_size = [img_height, img_width]
start_position = [0, 0]
end_position = [img_height, img_width]
fps = 30
rec_sec = 5

class mouseParam:
    def __init__(self, input_img_name):
        self.mouseEvent = {"x":None, "y":None, "event":None, "flags":None}
        cv2.setMouseCallback(input_img_name, self.__CallBackFunc, None)
    
    def __CallBackFunc(self, eventType, x, y, flags, userdata):
        self.mouseEvent["x"] = x
        self.mouseEvent["y"] = y
        self.mouseEvent["event"] = eventType    
        self.mouseEvent["flags"] = flags    
    
    def getEvent(self):
        return self.mouseEvent["event"]                

    def getPos(self):
        return self.mouseEvent["x"], self.mouseEvent["y"]
# -------------------------------------------

def drawCapRegion():
    img = cv2.imread("screen.png")
    cv2.imwrite("half_screen.png", 
                cv2.resize(cv2.rectangle(img, start_position, end_position, (0,255,0), 10),
                    None,fx=0.5,fy=0.5))
    
def capture():
    img_num = 0
    img_h = end_position[0] - start_position[0]
    img_w = end_position[1] - start_position[1]
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    date = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("frames", exist_ok=True)
    os.makedirs("videos", exist_ok=True)
    for file in glob.glob("frames/*.png"):
        if os.path.exists(file):
            os.remove(file)
    start_time = time.time()
    frames = []
    while time.time() - start_time < rec_sec:
        frames.append(pag.screenshot(region=(start_position[0], start_position[1], img_h, img_w)))
        print(time.time() - start_time)
        img_num+=1
    fps = img_num/rec_sec
    video = cv2.VideoWriter("videos/" + date + ".mp4", fourcc, fps, (img_h, img_w))
    img_num = 0
    for frame in frames:
        img_num += 1
        frame = np.array(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.imwrite("frames/{:010d}.png".format(img_num), frame)
        video.write(frame)
        
def mouse_callback():
    if event == cv2.EVENT_LBUTTONDOWN:
        print("clicked")

def clickPosition():
    img = cv2.imread("screen.png")
    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", mouse_callback)
    mouseData = mouseParam("Image")
    cv2.imshow("Image", img)
    cv2.moveWindow("Image", 0, 0)
    while True:
        cv2.waitKey(3)
        if mouseData.getEvent() == cv2.EVENT_LBUTTONDOWN:
            mx, my = mouseData.getPos()
            break
    cv2.destroyWindow("Image")
    return mx, my

def compare():
    if start_position[0] > end_position[0]:
        temp = start_position[0]
        start_position[0] = end_position[0]
        end_position[0] = temp
    elif start_position[0] == end_position[0]:
        if start_position[0] == 0:
            end_position[0]+=1
        elif end_position[0] == screen_size[0]:
            start_position[0]-=1
    if start_position[1] > end_position[1]:
        temp = start_position[1]
        start_position[1] = end_position[1]
        end_position[1] = temp
    elif start_position[1] == end_position[1]:
        if start_position[1] == 0:
            end_position[1]+=1
        elif end_position[1] == screen_size[1]:
            start_position[1]-=1

def setStartPosition():
    start_position[0], start_position[1] = clickPosition()
    compare()
    drawCapRegion()

def setEndPosition():
    end_position[0], end_position[1] = clickPosition()
    compare()
    drawCapRegion()

##### design GUI #####
# -------------------------------------------
sg.theme("DarkBlue")

timeText = sg.Text(f"capturing time : {rec_sec}", key = "-capturingTime-")
inputTime = sg.InputText(key = "-inputSecond-", size=(5,1))
setTime = sg.Button("set time", key = "-setSecond-")
FPSText = sg.Text(f"fps : {fps}")
screen = [sg.Image(filename = "./half_screen.png", key = "-imageReflesh-")]
set =  [
        sg.Button("setStart", key = "-setStart-"), 
        sg.Button("setEnd", key = "-setEnd-"),
        ]
finish = [sg.Button("finish", key = "-finish-", pad = ((0,0),(10)))]
screenSizeText = [sg.Text(f"screen size : {screen_size}", key = "-screenSize-")]
startPositionText = sg.Text(f"start position : {start_position}", key = "-startPosition-")
endPositionText = sg.Text(f"end position : {end_position}", key = "-endPosition-")
startCapture = [sg.Button("capture start!!", size = (15, 1), key = "-startCapture-")]

layout = [[
           screenSizeText,
           screen, 
           set, 
           [timeText, inputTime, setTime],
           [FPSText, startPositionText, endPositionText,],
           startCapture,
           finish,
           ]]

window = sg.Window("capture movie", layout, size=(1000,800))

drawCapRegion()

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == "-finish-":
        break
    if event == "setStart":
        setStartPosition()
    if event == "setEnd":
        setEndPosition()
    if event == "-startCapture-":
        capture()
    if event == "-setStart-":
        setStartPosition()
        window["-startPosition-"].update(f"start position : {start_position}")
        window["-imageReflesh-"].update(filename = "./half_screen.png")
    if event == "-setEnd-":
        setEndPosition()
        window["-endPosition-"].update(f"end position : {end_position}")
        window["-imageReflesh-"].update(filename = "./half_screen.png")
    if event == "-setSecond-":
        rec_sec = int(values["-inputSecond-"])
        window["-capturingTime-"].update(f"capturing time : {rec_sec}")
    
window.close()
# -------------------------------------------



