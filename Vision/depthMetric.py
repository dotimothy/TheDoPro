import cv2 as cv
import os
from time import time
import matplotlib.pyplot as plt
from matplotlib.pylab import cm
import numpy as np
import csv

image_L = cv.imread(f'../Images/L_25.png', 0)
image_R = cv.imread(f'../Images/R_25.png', 0)

stereo = cv.StereoBM_create(numDisparities=64, blockSize=15)
disparity = stereo.compute(image_L,image_R)
plt.imshow(disparity,cmap='jet')
plt.axis('off')
plt.savefig('./disMaps/D_50.png')


print(disparity[270][330])