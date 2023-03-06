# The Do-Pro Object Avoidance Detection System using ADAS

import customStereo as cs
import cv2 as cv 
import numpy as np
import colorsys
from time import sleep
import sys
if(sys.platform == 'linux'):
	import RPi.GPIO as GPIO

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
def classifyCenter(r,g,b,clusterCount,numPixels):
	if(r >= 1.25*g and r >= 1.25*b and clusterCount >= 0.25*numPixels):
		return 1
	elif(b >= g and b >= r):
		return 0
	return 0.5

# Calculates Clustering given Disparity Map for ADAS 
def ADASMapKMeans(disparity,K):
	pixels = np.float32(disparity.reshape((-1, 3)))

	criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 3*K, 1.0)

	comp, labels, centers = cv.kmeans(pixels, K, None, criteria, 10, cv.KMEANS_RANDOM_CENTERS)


	centers = np.uint8(centers)
	counts = np.bincount(labels.flatten())
	segmented = centers[labels.flatten()]
	segmented = segmented.reshape(disparity.shape)
	 
	return segmented,centers,counts



if __name__ == '__main__':
	# Parameters for the Simulation
	from math import *
	depths = [12,15,18,21,24,27,30,33,36]
	interval = 4
	counter = 0
	programMode = 0
	cs.adjustNumDisp(32)
	cs.adjustExposure(-4.0)
	# pins are physical	
	leds = {
		'flash': {'pin': 15},
		'capture':{'pin': 7}
	}
	if(sys.platform == 'linux'):
		GPIO.setwarnings(False)
		for led in leds:
			GPIO.setup(leds[led]['pin'],GPIO.OUT)
	while True:
		# Images
		left = cs.readLeft(programMode)
		right = cs.readRight(programMode)
		# Compute using OpenCV SGBM HeatMap
		disparityMap = cv.cvtColor(cs.processCapture(left,right,1,1,False,'jet'),cv.COLOR_BGR2RGB)
		#disparity = cv.imread('result2.jpg')
		disparityMap = disparityMap[:,64:disparityMap.shape[1]]
		numPixels = disparityMap.shape[0]*disparityMap.shape[1]
		#cv.imwrite('cropped.png',disparityMap)
		mapClusters, mapCenters, mapCounts = ADASMapKMeans(disparityMap,3)
		mapClassifications = []
		for i, center in enumerate(mapCenters):
			mapClassifications.append(classifyCenter(center[2],center[1],center[0],mapCounts[i],numPixels))
		detect = (True in (classification == 1 for classification in mapClassifications)) 
		if(sys.platform == 'win32'):
			cv.imshow('cluster',mapClusters)
			print(f'Detected: {detect}')
			print(mapClassifications)
			print(100*mapCounts/numPixels)
			print()
		elif(sys.platform == 'linux'):
				for led in leds: #Turns on Light if Detected.
					GPIO.output(leds[led]['pin'],1 if detect else 0)

		counter = counter  + 1
		cv.waitKey(1)
		
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

