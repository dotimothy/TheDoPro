import PIL
import matplotlib.pyplot as plt
import cv2 as cv
from time import time
import os

image_L = cv.imread('../Images/left_cone.png', 0)
image_R = cv.imread('../Images/right_cone.png', 0)

if(not os.path.exists('disMaps')):
	os.makedirs('./disMaps')

# plt.figure(figsize=(20, 10))
# plt.subplot(121)
# plt.imshow(image_L)
# plt.title('Left Image', fontsize=20)
# plt.subplot(122)
# plt.imshow(image_R)
# plt.title('Right Image', fontsize=20)
# plt.tight_layout()

# start = time()
# stereo = cv.StereoBM_create(numDisparities=64, blockSize=17)
# disparity = stereo.compute(image_L, image_R)
# end = time()

# plt.figure(figsize=(20, 10))
# plt.imshow(disparity, cmap='jet')
# plt.colorbar()

for i in range(5,255,2):
	start = time()
	stereo = cv.StereoBM_create(numDisparities=64, blockSize=i)
	disparity = stereo.compute(image_L, image_R)
	end = time()
	print(f'Finished in {1000*(end - start)} ms for blockSize = {i}') 
	plt.figure()
	plt.imshow(disparity, cmap='jet')
	plt.savefig(f'./disMaps/disMap_{i}.png')