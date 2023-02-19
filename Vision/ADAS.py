# Object Avoidance Detection System using ADAS

import customStereo as cs
import cv2 as cv 
from time import sleep

left = cs.readLeft(0)
right = cs.readRight(0)
disparity = cv.cvtColor(cs.processCapture(left,right,0,1),cv.COLOR_BGR2RGB)

close = cs.extractIntensity(disparity,170)
mid = cs.extractIntensity(disparity,130)
far = cs.extractIntensity(disparity,60)

cv.imshow('disparity',disparity)
cv.imshow('close',close)
cv.imshow('mid',mid)
cv.imshow('far',far)

cv.waitKey(30000)