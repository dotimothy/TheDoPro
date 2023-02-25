from time import time
import PIL
import matplotlib.pyplot as plt
import cv2 as cv
import os
import numpy as np
import customStereo as cs

leftCam = cv.VideoCapture(2)
rightCam = cv.VideoCapture(1)

# while True:
# 	leftCheck, leftFrame = leftCam.read()
# 	rightCheck, rightFrame = rightCam.read()
# 	leftFrame = cv.cvtColor(leftFrame,cv.COLOR_BGR2GRAY)
# 	rightFrame = cv.cvtColor(rightFrame,cv.COLOR_BGR2GRAY)

# 	start = time()
# 	stereo = cv.StereoBM_create(numDisparities=16, blockSize=15)
# 	disparity = stereo.compute(leftFrame, rightFrame)
# 	end = time() 

# 	cv.imshow('left', leftFrame)
# 	cv.imshow('right',rightFrame)
# 	cv.imshow('disparity',cv.applyColorMap((disparity).astype(np.uint8),cv.COLORMAP_JET))

# 	key = cv.waitKey(1)
# 	if key == 27:
# 	    break

leftCheck, leftFrame = leftCam.read()
rightCheck, rightFrame = rightCam.read()
leftFrame = cv.cvtColor(leftFrame,cv.COLOR_BGR2GRAY)
rightFrame = cv.cvtColor(rightFrame,cv.COLOR_BGR2GRAY)
scale = 1
leftFrame = cv.resize(leftFrame,(int(leftFrame.shape[1]/scale),int(leftFrame.shape[0]/scale)),interpolation=cv.INTER_CUBIC)
rightFrame = cv.resize(rightFrame,(int(rightFrame.shape[1]/scale),int(rightFrame.shape[0]/scale)),interpolation=cv.INTER_CUBIC)

start = time()
result = cs.vec_cost_block_matching(leftFrame, rightFrame, 9, 9, 16)
end = time()
disparity = result[0][:,:,0]
disparity = cv.resize(disparity,(disparity.shape[1]*scale,disparity.shape[0]*scale),interpolation=cv.INTER_CUBIC)
disparity = (2*disparity).astype(np.uint8)
print(f'Completed in {end-start} s')

cv.imshow('left', leftFrame)
cv.imshow('right',rightFrame)
cv.imshow('disparity',disparity)
cv.waitKey(5000)

leftCam.release()
rightCam.release()
cv.destroyAllWindows()
	