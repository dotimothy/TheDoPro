import cv2 as cv 
import numpy as np

def createGrid(width,height,sep,thickness,mode):
	if(mode == 0): # White Borders
		im = np.zeros((width,height)).astype(np.uint8)
		border = 255
	else: # Black Borders
		im = 255*np.ones((width,height)).astype(np.uint8)
		border = 0
	for i in range(0,width-thickness,sep): 
		for j in range(height):
			for k in range(thickness):
				im[i+k][j] = border
	for i in range(width):
		for j in range(0,height-thickness,sep):
			for k in range(thickness):
				im[i][j+k] = border
	return im

if __name__ == '__main__':
	grid = createGrid(1080,1920,256,64,1)
	cv.imshow('grid',grid)
	cv.imwrite('grid.png',grid)
	cv.waitKey(2000)