from time import time
import PIL
import matplotlib.pyplot as plt
import cv2 as cv
import os
import numpy as np
import customStereo as cs

leftCam = cv.VideoCapture(2)
rightCam = cv.VideoCapture(1)

while True:
	leftCheck, leftFrame = leftCam.read()
	rightCheck, rightFrame = rightCam.read()
	leftFrame = cv.cvtColor(leftFrame,cv.COLOR_BGR2GRAY)
	rightFrame = cv.cvtColor(rightFrame,cv.COLOR_BGR2GRAY)

	start = time()
	stereo = cv.StereoBM_create(numDisparities=16, blockSize=15)
	disparity = stereo.compute(leftFrame, rightFrame)
	end = time() 

	cv.imshow('left', leftFrame)
	cv.imshow('right',rightFrame)
	cv.imshow('disparity',cv.applyColorMap((disparity).astype(np.uint8),cv.COLORMAP_JET))

	key = cv.waitKey(1)
	if key == 27:
	    break


leftCam.release()
rightCam.release()
cv.destroyAllWindows()
	