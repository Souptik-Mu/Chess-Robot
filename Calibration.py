import cv2
import numpy as np

def empty(i):
    pass

path = "CBreal.jpg"
cap = cv2.VideoCapture(0)
cv2.namedWindow("TrackedBars")
cv2.resizeWindow("TrackedBars", 640, 340)



def on_trackbar(val):
    hue_min = cv2.getTrackbarPos("Hue Min", "TrackedBars")
    hue_max = cv2.getTrackbarPos("Hue Max", "TrackedBars")
    sat_min = cv2.getTrackbarPos("Sat Min", "TrackedBars")
    sat_max = cv2.getTrackbarPos("Sat Max", "TrackedBars")
    val_min = cv2.getTrackbarPos("Val Min", "TrackedBars")
    val_max = cv2.getTrackbarPos("Val Max", "TrackedBars")

    lower = np.array([hue_min, sat_min, val_min])
    upper = np.array([hue_max, sat_max, val_max])

    imgMASK = cv2.inRange(imgHSV, lower, upper)
    
    #_, imgMASK = cv2.threshold(imgHSV, Th_min, Th_max, cv2.THRESH_BINARY) #good at detecting black

    #cv2.imshow("Output1", img)
    #cv2.imshow("Output2", imgHSV)
    cv2.imshow("Mask", imgMASK)


cv2.createTrackbar("Hue Min", "TrackedBars", 0, 179, on_trackbar)
cv2.createTrackbar("Hue Max", "TrackedBars", 179, 179, on_trackbar)
cv2.createTrackbar("Sat Min", "TrackedBars", 0, 255, on_trackbar)
cv2.createTrackbar("Sat Max", "TrackedBars", 255, 255, on_trackbar)
cv2.createTrackbar("Val Min", "TrackedBars", 0, 255, on_trackbar)
cv2.createTrackbar("Val Max", "TrackedBars", 255, 255, on_trackbar)

#img = cv2.imread(path)
#imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)


if cap.isOpened() :
    while 1:
        global img
        ret, img = cap.read()
        global imgHSV
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        

        cv2.imshow('image',img)
        on_trackbar(0)
        
        #k= cv2.waitKey(1000) # it delays some milisec or until retrns a key stroke(-1 for none)
        if(not cv2.waitKey(200)) :
            break
# Show some stuff
#on_trackbar(0)
# Wait until user press some key
cv2.waitKey()