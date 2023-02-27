import cv2 as cv 
import numpy as np

def createGrid(width,height,sep,mode):
	if(mode == 0): # White Borders
		im = np.zeros((width,height)).astype(np.uint8)
		border = 255
	else:
		im = 255*np.ones((width,height)).astype(np.uint8)
		border = 0
	for i in range(0,width,sep): 
		for j in range(height):
			im[i][j] = border
	for i in range(width):
		for j in range(0,height,sep):
			im[i][j] = border
	return im

if __name__ == '__main__':
	grid = createGrid(1920,1080,16,1)
	cv.imshow('grid',grid)
	cv.waitKey(2000)