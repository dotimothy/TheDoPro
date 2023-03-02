# The Do-Pro Object Avoidance Detection System using ADAS

import customStereo as cs
import cv2 as cv 
import numpy as np
from time import sleep

# Calculates Density of Non-Zero Pixels
def calculateDensity(disparity):
	size = disparity.shape
	gray = cv.cvtColor(disparity,cv.COLOR_BGR2GRAY)
	pixelCount = 0
	for i in range(size[0]):
		for j in range(size[1]):
			if(gray[i][j] != 0):
				pixelCount = pixelCount + 1
	return pixelCount / size[0] / size[1]

def extractIntensity(disparity,intensity):
    gray = cv.cvtColor(disparity,cv.COLOR_BGR2GRAY)
    filtered = disparity.copy()
    for i in range(disparity.shape[0]): 
        for j in range(disparity.shape[1]):
            pixel = gray[i,j]
            if((pixel <= int(intensity-50) or pixel >= int(intensity+50))):
                filtered[i,j,2] = 0
                filtered[i,j,1] = 0
                filtered[i,j,0] = 0
    return filtered



if __name__ == '__main__':
	left = cs.rectifyLeft(cs.readLeft(0))
	right = cs.rectifyRight(cs.readRight(0))
	# Compute using OpenCV SGBM
	disparity = cv.cvtColor(cs.processCapture(left,right,1,1),cv.COLOR_BGR2RGB)

	close = extractIntensity(disparity,170)
	mid = extractIntensity(disparity,130)
	far = extractIntensity(disparity,60)
	print(calculateDensity(far), calculateDensity(mid), calculateDensity(close))

