import PIL
import matplotlib.pyplot as plt
from matplotlib.pylab import cm
import cv2 as cv
import time
import numpy as np
from scipy import ndimage as nd
from multiprocessing import Process, Queue
from os import cpu_count
import sys
from math import *

# Deprecated CUDA Support 
# haveGPU = False
# try:
#     import cupy as cp
#     haveGPU = True
# except:
#     print(f'No GPU Avaliable for cupy')

# Tries and Open the Cameras #
try:
    if(sys == 'win32'):
        leftCam = cv.VideoCapture(0,cv.CAP_DSHOW)
        rightCam = cv.VideoCapture(1,cv.CAP_DSHOW)
    else:
        leftCam = cv.VideoCapture(1)
        rightCam = cv.VideoCapture(2)
    leftCam.set(cv.CAP_PROP_SHARPNESS,200)
    rightCam.set(cv.CAP_PROP_SHARPNESS,200)
    leftCam.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    leftCam.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
    rightCam.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    rightCam.set(cv.CAP_PROP_FRAME_HEIGHT,480)
except:
    print(f'No Webcams')

#Open Stereo-Map
cv_file = cv.FileStorage()
cv_file.open('../Calibration/stereoMap_matlab.xml', cv.FileStorage_READ)

stereoMapL_x = cv_file.getNode('stereoMapL_x').mat()
stereoMapL_y = cv_file.getNode('stereoMapL_y').mat()
stereoMapR_x = cv_file.getNode('stereoMapR_x').mat()
stereoMapR_y = cv_file.getNode('stereoMapR_y').mat()

# OpenCV Stereo Objects
stereoBM = cv.StereoBM_create(numDisparities=128,blockSize=17)
stereoSGBM = cv.StereoSGBM_create(minDisparity=0, numDisparities=128, blockSize=9, P1=8*9*9, P2=32*9*9, disp12MaxDiff=1, uniquenessRatio=10, speckleWindowSize=50, speckleRange=32)

def vec_cost_block_matching(image_L_gray, image_R_gray, block_x, block_y, disp):

    # Image Dimension Specifications
    column_offset = np.floor(block_x/2).astype(int)
    row_offset = np.floor(block_y/2).astype(int)

    col_bound_L = column_offset + disp
    col_bound_U = image_L_gray.shape[1] - column_offset
    row_bound_L = row_offset
    row_bound_U = image_L_gray.shape[0] - row_offset
    rsize = image_L_gray.shape[1]

    # Define Vectorization Cost Function
    cost_vec = np.empty((row_bound_U-row_bound_L, col_bound_U-col_bound_L, disp))

    # Average Image
    L_avg = nd.uniform_filter(image_L_gray, (block_y, block_x), mode='constant')
    R_avg = nd.uniform_filter(image_R_gray, (block_y, block_x), mode='constant')

    # Define indicies
    idx = (np.arange(row_bound_L, row_bound_U)*rsize + \
            np.arange(col_bound_L, col_bound_U).reshape(-1, 1)).transpose()
    bead = (np.arange(-row_offset, row_offset+1)*rsize + \
            np.arange(-column_offset, column_offset+1).reshape(-1, 1)).reshape(-1, 1)

    # Perform cost caluclation on left image
    L_string = idx.flatten()
    L_braid  = L_string + bead
    L_cost_str = (image_L_gray).flatten()[L_braid.flatten()].reshape(L_braid.shape)
    L_avg_str = L_avg.flatten()[L_string.flatten()]
    L_residual = (L_cost_str - L_avg_str)
    L2_cost = (L_residual**2).sum(axis=0).reshape(idx.shape)

    # Perform cost caluclation on right image
    for d in range(0, disp):

      R_string = (idx - d).flatten()
      R_braid  = L_string + bead
      R_cost_str = (image_R_gray).flatten()[R_braid.flatten()].reshape(R_braid.shape)
      R_avg_str = R_avg.flatten()[R_string.flatten()]
      R_residual = (R_cost_str - R_avg_str)
      R2_cost = (R_residual**2).sum(axis=0).reshape(idx.shape)

      LR_cost_str = L_residual*R_residual
      LR_cost = LR_cost_str.sum(axis=0).reshape(idx.shape)
      
      cost_vec[:, :, d] = LR_cost/np.sqrt(L2_cost*R2_cost)

    return cost_vec, row_bound_U-row_bound_L, col_bound_U-col_bound_L

def multiblock(image_L_gray, image_R_gray, block1_x, block1_y, block2_x, block2_y, block3_x, block3_y, disp):

    triblock = np.zeros(np.append(image_L_gray.shape, 3))

    block1, row_size_1, col_size_1 = vec_cost_block_matching(image_L_gray, image_R_gray, block1_x, block1_y, disp)
    block2, row_size_2, col_size_2 = vec_cost_block_matching(image_L_gray, image_R_gray, block2_x, block2_y, disp)
    block3, row_size_3, col_size_3 = vec_cost_block_matching(image_L_gray, image_R_gray, block3_x, block3_y, disp)

    R1 = (image_L_gray.shape[0] - row_size_1 - np.floor(block1_y/2))
    R2 = (image_L_gray.shape[0] - row_size_2 - np.floor(block2_y/2))
    R3 = (image_L_gray.shape[0] - row_size_3 - np.floor(block3_y/2))
    R1 = int(R1)
    R2 = int(R2)
    R3 = int(R3)

    C1 = (image_L_gray.shape[1] - col_size_1 - np.floor(block1_x/2) - 8)
    C2 = (image_L_gray.shape[1] - col_size_2 - np.floor(block2_x/2) - 8)
    C3 = (image_L_gray.shape[1] - col_size_3 - np.floor(block3_x/2) - 8)
    C1 = int(C1)
    C2 = int(C2)
    C3 = int(C3)

    triblock[R1:-R1, C1:-C1, 0] = block1[:, :, 0]
    triblock[R2:-R2, C2:-C2, 1] = block2[:, :, 0]
    triblock[R3:-R3, C3:-C3, 2] = block3[:, :, 0]

    triblock = np.prod(triblock, 2)

    return triblock

def costco_r_us(queue, disp_idx, num_disp, procs,image_R_gray,row_bound_U,row_bound_L,col_bound_U,col_bound_L,idx,L_string,bead,R_avg,L_residual,L2_cost):

    # Disp to run
    disps = range(disp_idx, num_disp, procs)

    # Define Vectorization Cost Function
    cost_vec = np.empty((row_bound_U-row_bound_L, col_bound_U-col_bound_L, len(disps)))

    # Computing disparity at specified index
    R_string = (idx - disp_idx).flatten()
    R_braid  = L_string + bead
    R_cost_str = (image_R_gray).flatten()[R_braid.flatten()].reshape(R_braid.shape)
    R_avg_str = R_avg.flatten()[R_string.flatten()]
    R_residual = (R_cost_str - R_avg_str)
    R2_cost = (R_residual**2).sum(axis=0).reshape(idx.shape)
    LR_cost_str = L_residual*R_residual
    LR_cost = LR_cost_str.sum(axis=0).reshape(idx.shape)
    cost_vec = LR_cost/np.sqrt(L2_cost*R2_cost)

    #Return calculated disparity to queue
    return queue.put(cost_vec)

def mp_cost_block(image_L_gray, image_R_gray, block_x, block_y, disp, procs):

    # Define Multiprocessing
    q = Queue()
    disp_map = []
    processes = []

    # Image Dimension Specifications
    column_offset = np.floor(block_x/2).astype(int)
    row_offset = np.floor(block_y/2).astype(int)

    col_bound_L = column_offset + disp
    col_bound_U = image_L_gray.shape[1] - column_offset
    row_bound_L = row_offset
    row_bound_U = image_L_gray.shape[0] - row_offset
    rsize = image_L_gray.shape[1]

    # Define Vectorization Cost Function
    cost_vec = np.empty((row_bound_U-row_bound_L, col_bound_U-col_bound_L, procs))

    # Average Image
    L_avg = nd.uniform_filter(image_L_gray, (block_y, block_x), mode='constant')
    R_avg = nd.uniform_filter(image_R_gray, (block_y, block_x), mode='constant')

    # Define indicies
    idx = (np.arange(row_bound_L, row_bound_U)*rsize + \
            np.arange(col_bound_L, col_bound_U).reshape(-1, 1)).transpose()
    bead = (np.arange(-row_offset, row_offset+1)*rsize + \
            np.arange(-column_offset, column_offset+1).reshape(-1, 1)).reshape(-1, 1)

    # Perform cost caluclation on left image
    L_string = idx.flatten()
    L_braid  = L_string + bead
    L_cost_str = (image_L_gray).flatten()[L_braid.flatten()].reshape(L_braid.shape)
    L_avg_str = L_avg.flatten()[L_string.flatten()]
    L_residual = (L_cost_str - L_avg_str)
    L2_cost = (L_residual**2).sum(axis=0).reshape(idx.shape)

    for i in range(0, procs):
        p = Process(target=costco_r_us, args = [q, i, disp, procs,image_R_gray,row_bound_U,row_bound_L,col_bound_U,col_bound_L,idx,L_string,bead,R_avg,L_residual,L2_cost])
        p.start()
        processes.append(p)

    i = 0
    for p in processes:
        cost_vec[:, :, i] = q.get()
        i = i + 1

    for p in processes:
        p.join()

    cost = np.max(cost_vec, axis=2)

    return cost

def vec_cost_block_matching_gpu(image_L_gray, image_R_gray, block_x, block_y, disp):

    # Image Dimension Specifications
    column_offset = cp.floor(block_x/2).astype(int)
    row_offset = cp.floor(block_y/2).astype(int)

    col_bound_L = column_offset + disp
    col_bound_U = image_L_gray.shape[1] - column_offset
    row_bound_L = row_offset
    row_bound_U = image_L_gray.shape[0] - row_offset
    rsize = image_L_gray.shape[1]

    # Define Vectorization Cost Function
    cost_vec = cp.empty((row_bound_U-row_bound_L, col_bound_U-col_bound_L, disp))

    # Average Image
    L_avg = nd.uniform_filter(image_L_gray, (block_y, block_x), mode='constant')
    R_avg = nd.uniform_filter(image_R_gray, (block_y, block_x), mode='constant')

    # Define indicies
    idx = (cp.arange(row_bound_L, row_bound_U)*rsize + \
            cp.arange(col_bound_L, col_bound_U).reshape(-1, 1)).transpose()
    bead = (cp.arange(-row_offset, row_offset+1)*rsize + \
            cp.arange(-column_offset, column_offset+1).reshape(-1, 1)).reshape(-1, 1)

    # Perform cost caluclation on left image
    L_string = idx.flatten()
    L_braid  = L_string + bead
    L_cost_str = (image_L_gray).flatten()[L_braid.flatten()].reshape(L_braid.shape)
    L_avg_str = L_avg.flatten()[L_string.flatten()]
    L_residual = (L_cost_str - L_avg_str)
    L2_cost = (L_residual**2).sum(axis=0).reshape(idx.shape)

    # Perform cost caluclation on right image
    for d in range(0, disp):

      R_string = (idx - d).flatten()
      R_braid  = L_string + bead
      R_cost_str = (image_R_gray).flatten()[R_braid.flatten()].reshape(R_braid.shape)
      R_avg_str = R_avg.flatten()[R_string.flatten()]
      R_residual = (R_cost_str - R_avg_str)
      R2_cost = (R_residual**2).sum(axis=0).reshape(idx.shape)

      LR_cost_str = L_residual*R_residual
      LR_cost = LR_cost_str.sum(axis=0).reshape(idx.shape)
      
      cost_vec[:, :, d] = LR_cost/cp.sqrt(L2_cost*R2_cost)

    return cost_vec, row_bound_U-row_bound_L, col_bound_U-col_bound_L

def multiblock_gpu(image_L_gray, image_R_gray, block1_x, block1_y, block2_x, block2_y, block3_x, block3_y, disp):

    triblock = cp.zeros(cp.append(image_L_gray.shape, 3))

    block1, row_size_1, col_size_1 = vec_cost_block_matching(image_L_gray, image_R_gray, block1_x, block1_y, disp)
    block2, row_size_2, col_size_2 = vec_cost_block_matching(image_L_gray, image_R_gray, block2_x, block2_y, disp)
    block3, row_size_3, col_size_3 = vec_cost_block_matching(image_L_gray, image_R_gray, block3_x, block3_y, disp)

    R1 = (image_L_gray.shape[0] - row_size_1 - cp.floor(block1_y/2))
    R2 = (image_L_gray.shape[0] - row_size_2 - cp.floor(block2_y/2))
    R3 = (image_L_gray.shape[0] - row_size_3 - cp.floor(block3_y/2))
    R1 = int(R1)
    R2 = int(R2)
    R3 = int(R3)

    C1 = (image_L_gray.shape[1] - col_size_1 - cp.floor(block1_x/2) - 8)
    C2 = (image_L_gray.shape[1] - col_size_2 - cp.floor(block2_x/2) - 8)
    C3 = (image_L_gray.shape[1] - col_size_3 - cp.floor(block3_x/2) - 8)
    C1 = int(C1)
    C2 = int(C2)
    C3 = int(C3)

    triblock[R1:-R1, C1:-C1, 0] = block1[:, :, 0]
    triblock[R2:-R2, C2:-C2, 1] = block2[:, :, 0]
    triblock[R3:-R3, C3:-C3, 2] = block3[:, :, 0]

    triblock = cp.prod(triblock, 2)

    return triblock

def vec_NCC(image_L_gray, image_R_gray, block_x, block_y, disp):

    image_L_gray = image_L_gray + 1e-9
    image_R_gray = image_R_gray + 1e-9

    # Image Dimension Specifications
    column_offset = np.floor(block_x/2).astype(int)
    row_offset = np.floor(block_y/2).astype(int)

    col_bound_L = column_offset + disp
    col_bound_U = image_L_gray.shape[1] - column_offset
    row_bound_L = row_offset
    row_bound_U = image_L_gray.shape[0] - row_offset
    rsize = image_L_gray.shape[1]

    # Define Vectorization Cost Function
    ncc = np.empty((row_bound_U-row_bound_L, col_bound_U-col_bound_L, disp))

    # Average Image
    L_avg = nd.uniform_filter(image_L_gray, (block_y, block_x), mode='constant')
    R_avg = nd.uniform_filter(image_R_gray, (block_y, block_x), mode='constant')

    # Define indicies
    idx = (np.arange(row_bound_L, row_bound_U)*rsize + \
            np.arange(col_bound_L, col_bound_U).reshape(-1, 1)).transpose()
    bead = (np.arange(-row_offset, row_offset+1)*rsize + \
            np.arange(-column_offset, column_offset+1).reshape(-1, 1)).reshape(-1, 1)

    # Perform cost caluclation on left image
    L_string = idx.flatten()
    L_braid  = L_string + bead
    L_cost_str = (image_L_gray).flatten()[L_braid.flatten()].reshape(L_braid.shape)
    L_avg_str = L_avg.flatten()[L_string.flatten()]
    L_residual = (L_cost_str - L_avg_str)
    L2_cost = (L_residual**2).sum(axis=0).reshape(idx.shape)

    # Perform cost caluclation on right image
    for d in range(0, disp):

      R_string = (idx - d).flatten()
      R_braid  = L_string + bead
      R_cost_str = (image_R_gray).flatten()[R_braid.flatten()].reshape(R_braid.shape)
      R_avg_str = R_avg.flatten()[R_string.flatten()]
      R_residual = (R_cost_str - R_avg_str)
      R2_cost = (R_residual**2).sum(axis=0).reshape(idx.shape)

      LR_cost_str = L_residual*R_residual
      LR_cost = LR_cost_str.sum(axis=0).reshape(idx.shape)
      
      ncc[:, :, d] = LR_cost/(np.sqrt(L2_cost*R2_cost)+1e-2)

    #cost_vec = nd.uniform_filter(cost_vec, (block_y, block_x, 1), mode='constant') * block_x * block_y
    #cost_vec = np.max(cost_vec, axis=2)

    ncc = np.max(nd.uniform_filter(ncc, (17, 17, 1), mode='constant'), 2)

    return ncc

counter = 0
depths = [200,150,75,50]
def readLeft(mode):
    if(mode == 0): #Dev, Will Be an Image
        global counter
        counter = counter + 1
        return cv.cvtColor(cv.imread(f'../Images/L_{str(depths[trunc((counter % 16)/4)])}.png',1),cv.COLOR_BGR2RGB)
    elif(mode == 1): #Webcam
        return cv.cvtColor(leftCam.read()[1],cv.COLOR_BGR2RGB)

def readRight(mode):
    if(mode == 0): #Dev, Will Be an Image
        global counter
        counter = counter + 1
        return cv.cvtColor(cv.imread(f'../Images/R_{str(depths[trunc((counter % 16)/4)])}.png',1),cv.COLOR_BGR2RGB)
    elif(mode == 1): #Webcam
        return cv.cvtColor(rightCam.read()[1],cv.COLOR_BGR2RGB)

def correctPosition():
    global leftCam
    global rightCam
    temp = leftCam
    leftCam = rightCam
    rightCam = temp

def adjustExposure(exposure):
    leftCam.set(cv.CAP_PROP_EXPOSURE,exposure)
    rightCam.set(cv.CAP_PROP_EXPOSURE,exposure)

def rectifyLeft(leftFrame):
    return cv.remap(leftFrame,stereoMapL_x,stereoMapL_y,cv.INTER_LANCZOS4, cv.BORDER_CONSTANT, 0)

def rectifyRight(rightFrame):
    return cv.remap(rightFrame,stereoMapR_x,stereoMapR_y,cv.INTER_LANCZOS4, cv.BORDER_CONSTANT, 0)

def processCapture(leftFrame,rightFrame,algor,downscale):
    leftFrameGray = cv.cvtColor(leftFrame, cv.COLOR_BGR2GRAY)
    rightFrameGray = cv.cvtColor(rightFrame, cv.COLOR_BGR2GRAY)
    if(algor != 0 and algor != 1):
        leftFrameGray = leftFrameGray + 1e-1
        rightFrameGray = rightFrameGray + 1e-1
    if(downscale != 1):
        leftFrameGray = cv.resize(leftFrameGray,(int(leftFrameGray.shape[1]/downscale),int(leftFrameGray.shape[0]/downscale)),interpolation=cv.INTER_CUBIC)
        rightFrameGray = cv.resize(rightFrameGray,(int(rightFrameGray.shape[1]/downscale),int(rightFrameGray.shape[0]/downscale)),interpolation=cv.INTER_CUBIC)
    if(algor == 0): #OpenCV Block Matching
        disparity = stereoBM.compute(leftFrameGray,rightFrameGray)      
        disparity = ((disparity+16)/4 - 1).astype(np.uint8)
    elif(algor == 1): #OpenCV Semi-Global Block Matching
        disparity = stereoSGBM.compute(leftFrameGray,rightFrameGray)      
        disparity = ((disparity+16)/4 - 1).astype(np.uint8)
    elif(algor == 2): #Cost Block Matching
        result = vec_cost_block_matching(leftFrameGray, rightFrameGray, 9, 9, 16)
        disparity = result[0][:,:,0]
    elif(algor == 3): #Multiblock
        disparity = multiblock(leftFrameGray, rightFrameGray, 9, 9, 21, 3, 3, 21, 16)
    elif(algor == 4): #Multiprocess Cost Block
        disparity = mp_cost_block(leftFrameGray,rightFrameGray,9, 9, 16, cpu_count())
    elif(algor == 5): #NCC Cost Block
        disparity = vec_NCC(leftFrameGray,rightFrameGray,3,3,32)
    elif(algor == 6): #Cost Block Matching GPU
        if(haveGPU):
            result = vec_cost_block_matching_gpu(leftFrameGray, rightFrameGray, 9, 9, 8)
        else:
            print(f'No GPU: Fallback to CPU Computation')
            result = vec_cost_block_matching(leftFrameGray, rightFrameGray, 9, 9, 8)
        disparity = result[0][:,:,0]
    elif(algor == 7): #Multiblock GPU
        if(haveGPU): 
            result = multiblock_gpu(leftFrameGray,rightFrameGray,9,9,21,3,3,21,16)
        else:
            print(f'No GPU: Fallback to CPU Computation')
            disparity = multiblock(leftFrameGray, rightFrameGray, 9, 9, 21, 3, 3, 21, 16)
    if(downscale != 1):
        disparity = cv.resize(disparity,(disparity.shape[1]*downscale,disparity.shape[0]*downscale),interpolation=cv.INTER_CUBIC)
    disparity = cv.cvtColor(np.uint8(cm.jet(disparity)*255),cv.COLOR_RGBA2BGR)
    return disparity

def extractIntensity(disparity,intensity):
    gray = cv.cvtColor(disparity,cv.COLOR_BGR2GRAY)
    filtered = disparity.copy()
    for i in range(disparity.shape[0]): 
        for j in range(disparity.shape[1]):
            pixel = gray[i,j]
            if((pixel <= int(intensity-50) or pixel >= int(intensity+50))):
                filtered[i,j,2] = 0
                filtered[i,j,1] = 0
                filtered[i,j,0] = 0
    return filtered


if __name__ == "__main__":
    image_L = cv.imread('../Images/tim_L.png',0)
    image_L = cv.cvtColor(image_L, cv.COLOR_BGR2RGB)
    image_R = cv.imread('../Images/tim_R.png', 0)
    image_R = cv.cvtColor(image_R, cv.COLOR_BGR2RGB)
    # image_L = readLeft(1)
    # image_R = readRight(1)
    start = time.time()
    disparity = cv.cvtColor(processCapture(image_L,image_R,1,1),cv.COLOR_BGR2RGB)
    #disparity = cv.imread('../Images/openCV.png')
    #test = cv.cvtColor(test,cv.COLOR_BGR2RGB)
    #stereo = cv.StereoBM_create(numDisparities=64, blockSize=9)
    #test = stereo.compute(image_L, image_R)
    print(f'Finished in {time.time() - start} seconds')
    cv.imshow('result',disparity)
    cv.imwrite('./result.png',disparity)
    cv.waitKey(2000)


    # image_L = cv.imread('../Images/left_piano.png', 1)
    # image_L = cv.cvtColor(image_L, cv.COLOR_BGR2RGB)
    # image_R = cv.imread('../Images/right_piano.png', 1)
    # image_R = cv.cvtColor(image_R, cv.COLOR_BGR2RGB)

    # image_L_gray = cv.cvtColor(image_L, cv.COLOR_BGR2GRAY) + 1e-1
    # image_R_gray = cv.cvtColor(image_R, cv.COLOR_BGR2GRAY) + 1e-1

    # downscale = 2
    # image_L_gray = cv.resize(image_L_gray,(int(image_L_gray.shape[1]/downscale),int(image_L_gray.shape[0]/downscale)))
    # image_R_gray = cv.resize(image_R_gray,(int(image_R_gray.shape[1]/downscale),int(image_R_gray.shape[0]/downscale)))

    # start = time.time() 
    # BM  = vec_cost_block_matching(image_L_gray, image_R_gray, 9, 9, 16)
    # print(f'Vectorized Block Matching: {round(time.time()-start,2)} s')
    # start = time.time()
    # MBM = multiblock(image_L_gray, image_R_gray, 9, 9, 21, 3, 3, 21, 16)
    # print(f'Vectorized Multiblock: {round(time.time()-start,2)} s')

    # #BM = cv.resize(BM, (BM.shape[1]*downscale,BM.shape[0]*downscale))
    # #MBM = cv.resize(MBM,(MBM.shape[1]*downscale,MBM.shape[0]*downscale))

    # plt.figure(figsize=(30, 15))
    # plt.subplot(321)
    # plt.imshow(image_L)
    # plt.title('Left Image', fontsize=20)
    # plt.subplot(322)
    # plt.imshow(image_R)
    # plt.title('Right Image', fontsize=20)
    # plt.subplot(323)
    # plt.imshow(image_L_gray, cmap='gray')
    # plt.title('Left Image - Gray', fontsize=20)
    # plt.subplot(324)
    # plt.imshow(image_R_gray, cmap='gray')
    # plt.title('Right Image - Gray', fontsize=20)
    # plt.subplot(325)
    # plt.imshow(BM[0][:, :, 0], cmap='jet')
    # plt.title('Disparity Map (9x9)', fontsize=20)
    # plt.subplot(326)
    # plt.imshow(MBM, cmap='jet')
    # plt.title('Disparity Map (Multi-block)', fontsize=20)
    # plt.tight_layout(w_pad=-60)
    # plt.savefig('result.png')

    # # cv.imwrite('cost.png',cv.applyColorMap((255*BM[0][:,:,0]/max(BM)).astype(np.uint8),cv.COLORMAP_JET))
    # # cv.imwrite('multi.png',cv.applyColorMap(MBM.astype(np.uint8),cv.COLORMAP_JET))

# else: 
#     try:
#         leftCam = cv.VideoCapture(0)
#         rightCam = cv.VideoCapture(2)
#     except:
#         print(f'No Webcams')
