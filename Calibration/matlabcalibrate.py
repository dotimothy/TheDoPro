import cv2 as cv
import scipy.io as io
import numpy as np


openCV = io.loadmat('openCV.mat')
size = (640,480)
rectifyScale = 1
out = (0,0)
openCV['translate'] = np.transpose(openCV['translate'])


#print(openCV['intrinsicL'],"\n\n",openCV['distortL'],"\n\n",openCV['intrinsicR'],"\n\n",openCV['distortR'],"\n\n",size,"\n\n",openCV['rotate'],"\n\n",openCV['translate'],"\n\n",recitfyScale,"\n\n",out)
R_L, R_R, P_L, P_R, Q, roi_L, roi_R = cv.stereoRectify(openCV['intrinsicL'], openCV['distortL'], openCV['intrinsicR'], openCV['distortR'], size, openCV['rotate'], openCV['translate'], rectifyScale, out)

stereoMapL = cv.initUndistortRectifyMap(openCV['intrinsicL'], openCV['distortL'], R_L, P_L, size, cv.CV_16SC2)
stereoMapR = cv.initUndistortRectifyMap(openCV['intrinsicR'], openCV['distortR'], R_R, P_R, size, cv.CV_16SC2)

print("Saving MATLAB stereo parameters!")
cv_file = cv.FileStorage('stereoMap_matlab.xml', cv.FILE_STORAGE_WRITE)

cv_file.write('stereoMapL_x',stereoMapL[0])
cv_file.write('stereoMapL_y',stereoMapL[1])
cv_file.write('stereoMapR_x',stereoMapR[0])
cv_file.write('stereoMapR_y',stereoMapR[1])

cv_file.release()