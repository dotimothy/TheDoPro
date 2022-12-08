import cv2 as cv
import os
from time import time
import matplotlib.pyplot as plt
from matplotlib.pylab import cm
import numpy as np

#objects = ['art','chess','cone','curule','mask','piano']
objects = ['piano']
if(not os.path.exists('./disMaps')):
	os.mkdir('./disMaps')

for item in objects:
	image_L = cv.imread(f'../Images/left_{item}.png', 0)
	image_R = cv.imread(f'../Images/right_{item}.png', 0)

	if(not os.path.exists(f'./disMaps/{item}')):
		os.mkdir(f'./disMaps/{item}')
	for i in range(0,5): #Up to 256 Disparities
		disp = 16 * (2**i)
		start = time()
		stereo = cv.StereoBM_create(numDisparities=disp, blockSize=9)
		disparity = stereo.compute(image_L, image_R)
		end = time()
		print(f'{item}: Finished in {1000*(end - start)} ms for Disparity = {disp}') 
		disparity = ((disparity+16)/4 - 1).astype(np.uint8)
		disparity = cv.cvtColor(np.uint8(cm.jet(disparity)*255),cv.COLOR_RGBA2BGR)
		cv.imwrite(f'./disMaps/{item}/disp_{disp}.png',disparity)