# The Do-Pro Object Avoidance Detection System using ADAS

import customStereo as cs
import cv2 as cv 
import numpy as np
import colorsys
from time import sleep

# Calculates Density of Non-Zero Pixels
def calculateDensity(image):
	size = image.shape
	if(len(size)==3):
		gray = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
	else:
		gray = image
	pixelCount = 0
	for i in range(size[0]):
		for j in range(size[1]):
			if(gray[i][j] != 0):
				pixelCount = pixelCount + 1
	return pixelCount / size[0] / size[1]

# Segment given image and desired gray level
def extractIntensity(image,intensity):
	size = image.shape
	if(len(size)==3):
		gray = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
	else:
		gray = image
	filtered = image.copy()
	for i in range(size[0]):
		for j in range(size[1]):	
			pixel = gray[i,j]
			assign = abs(pixel-intensity) <= 25
			if(len(size)==3):
				filtered[i,j,2] = 255*assign
				filtered[i,j,1] = 255*assign
				filtered[i,j,0] = 255*assign
			else: 
				filtered[i,j] = 255*assign
	return filtered

#Classify K-Means center as being a cluster that's either close,far,or in-between
#Return: 0 - far, 0.5 - middle, 1 - close,
def classifyCenter(r,g,b):
	if(r >= 1.75*g and r >= 1.75*b):
		return 1
	elif(b >= g and b >= r):
		return 0
	return 0.5

# Calculates Clustering given Disparity for ADAS 
def ADASKMeans(disparity,K):
	pixels = np.float32(disparity.reshape((-1, 3)))

	criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 3*K, 1.0)

	comp, labels, centers = cv.kmeans(pixels, K, None, criteria, 10, cv.KMEANS_RANDOM_CENTERS)

	centers = np.uint8(centers)
	segmented = centers[labels.flatten()]
	segmented = segmented.reshape(disparity.shape)
	 
	return segmented,centers



if __name__ == '__main__':
	num = 0
	while num < 1:
		left = cs.rectifyLeft(cs.readLeft(0))
		right = cs.rectifyRight(cs.readRight(0))
		# Compute using OpenCV SGBM
		disparity = cv.cvtColor(cs.processCapture(left,right,1,1),cv.COLOR_BGR2RGB)
		#disparity = cv.imread('result2.jpg')
		disparity = disparity[:,256:disparity.shape[1]]
		cv.imwrite('cropped.png',disparity)
		clusters, centers = ADASKMeans(disparity,3)
		cv.imshow('cluster',clusters)
		classifications = []
		for center in centers:
			classifications.append(classifyCenter(center[2],center[1],center[0]))
		detect = True in (classification == 1 for classification in classifications)
		print(f'Detected: {detect}')
		num = num + 1
		cv.waitKey(5)
		
	# close = extractIntensity(clusters,0)
	# mid = extractIntensity(clusters,128)
	# far = extractIntensity(clusters,255)
	# cv.imshow('cluster',clusters)
	# cv.waitKey(1000)	
	# cv.imshow('close',close)
	# cv.waitKey(1000)
	# cv.imshow('mid',mid)
	# cv.waitKey(1000)
	# cv.imshow('far',far)
	# cv.waitKey(1000)
	#cv.imwrite('cluster.png',clusters)
	#print(calculateDensity(far), calculateDensity(mid), calculateDensity(close))

