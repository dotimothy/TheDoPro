import cv2 as cv
import os
from time import time
import matplotlib.pyplot as plt
from matplotlib.pylab import cm
import numpy as np
import csv

#objects = ['art','chess','cone','curule','mask','piano']
#objects = ['piano']
depths = [25,50,75,100,150,200]
if(not os.path.exists('./disMaps')):
	os.mkdir('./disMaps')


for depth in depths:
	image_L = cv.imread(f'../Images/L_{depth}.png', 0)
	image_R = cv.imread(f'../Images/R_{depth}.png', 0)
	entrylist = []

	if(not os.path.exists(f'./disMaps/Z_{depth}')):
		os.mkdir(f'./disMaps/Z_{depth}')
	for i in range(5,53,4): #Up to 256 Disparities
		entry = []
		entry.append(i)
		stereo = cv.StereoBM_create(numDisparities=32, blockSize=i)
		
		# Time Metric
		start = time()
		disparity = stereo.compute(image_L, image_R)
		comp = 1000*(time() - start)
		disparity = ((disparity+16)/4 - 1).astype(np.uint8)
		disparity = cv.cvtColor(np.uint8(cm.jet(disparity)*255),cv.COLOR_RGBA2RGB)
		entry.append(comp)
		entrylist.append(entry)

		#Saving Disparity to File 
		cv.imwrite(f'./disMaps/Z_{depth}/block{i}.png',disparity)
		print(f'{depth} in.: Finished in {comp} ms for Block = {i}')
	#Computation Calculation 
	headers = ['Block Size','Computation Time (ms)']
	file = open(f'./disMaps/Z_{depth}.csv','w',newline='')
	csvwriter = csv.writer(file)
	csvwriter.writerow(headers)
	csvwriter.writerows(entrylist)
	file.close()