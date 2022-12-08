import cv2 as cv
import os
from time import time
import matplotlib.pyplot as plt
from matplotlib.pylab import cm
import numpy as np
import csv

#objects = ['art','chess','cone','curule','mask','piano']
objects = ['piano']
if(not os.path.exists('./disMaps')):
	os.mkdir('./disMaps')

for item in objects:
	image_L = cv.imread(f'../Images/left_{item}.png', 0)
	image_R = cv.imread(f'../Images/right_{item}.png', 0)
	GT_L = cv.imread(f'../Images/left_{item}_GT.jpg',0)
	GT_R = cv.imread(f'../Images/right_{item}_GT.jpg',0)
	GT_L_Norm = (GT_L).astype(np.float)/np.max(GT_L)
	GT_R_Norm = (GT_R).astype(np.float)/np.max(GT_R)

	blocks = []
	times = []

	if(not os.path.exists(f'./disMaps/{item}')):
		os.mkdir(f'./disMaps/{item}')
	for i in range(5,51,2): #Up to 256 Disparities
		blocks.append(i)
		stereo = cv.StereoBM_create(numDisparities=64, blockSize=i)
		
		# Time Metric
		start = time()
		disparity = stereo.compute(image_L, image_R)
		disparity = ((disparity+16)/4 - 1).astype(np.uint8)
		disparity = cv.resize(disparity,(2820,1920),interpolation=cv.INTER_LINEAR)
		comp = time() - start
		times.append(comp)
		
		#Error Metric
		disp_Norm = (disparity.astype(np.float))/np.max(disparity)
		err_L = 100 * np.absolute(np.divide(np.subtract(disp_Norm,GT_L_Norm),GT_L_Norm)) 
		err_R = 100 * np.absolute(np.divide(np.subtract(disp_Norm,GT_R_Norm),GT_R_Norm))
		avg_err_L = np.average(err_L)
		avg_err_R = np.average(err_R)

		#Saving Disparity to File 
		cv.imwrite(f'./disMaps/{item}/block{i}.png',disparity)
		print(f'{item}: Finished in {1000*(comp)} ms for Block = {i}')
		print(f'{item} avereage error with left GT: {avg_err_L}%') 
		print(f'{item} avereage error with right GT: {avg_err_R}%') 