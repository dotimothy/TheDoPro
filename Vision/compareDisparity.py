import cv2 as cv
import os
from time import time
import matplotlib.pyplot as plt


#objects = ['art','chess','cone','curule','mask','piano']
objects = ['motorcycle']
if(not os.path.exists('./disMaps')):
	os.mkdir('./disMaps')

for item in objects:
	image_L = cv.imread(f'../Images/left_{item}.png', 0)
	image_R = cv.imread(f'../Images/right_{item}.png', 0)

	if(not os.path.exists(f'./disMaps/{item}')):
		os.mkdir(f'./disMaps/{item}')
	for i in range(0,5): #Up to 256 Disparities
		disp = 16 * (2**i)	
		if(not os.path.exists(f'./disMaps/{item}/disp{disp}')):
			os.mkdir(f'./disMaps/{item}/disp{disp}')
		for block in range(5,53,2): #Up to Block Size 51
			start = time()
			stereo = cv.StereoBM_create(numDisparities=disp, blockSize=block)
			disparity = stereo.compute(image_L, image_R)
			end = time()
			print(f'{item}: Finished in {1000*(end - start)} ms for Disparity = {disp} &  blockSize = {block}') 
			plt.figure(frameon=False)
			plt.axis('off')
			plt.imshow(disparity, cmap='jet')
			plt.savefig(f'./disMaps/{item}/disp{disp}/block{block}.png')
			plt.close()