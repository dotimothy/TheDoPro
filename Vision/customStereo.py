import PIL
import matplotlib.pyplot as plt
import cv2 as cv
import time
import numpy as np
from scipy import ndimage as nd

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

def readLeft():
    image_L = cv.imread('../Images/left_piano.png',1)
    cv.imshow('leftPreview',image_L)
    cv.waitKey(10)

def readRight():
    image_R = cv.imread('../Images/right_piano.png',1)
    cv.imshow('rightPreview',image_R)
    cv.waitKey(10)

def processCapture(algor,downscale):
    image_L = cv.imread('../Images/left_piano.png', 1)
    image_L = cv.cvtColor(image_L, cv.COLOR_BGR2RGB)
    image_R = cv.imread('../Images/right_piano.png', 1)
    image_R = cv.cvtColor(image_R, cv.COLOR_BGR2RGB)
    image_L_gray = cv.cvtColor(image_L, cv.COLOR_BGR2GRAY) + 1e-1
    image_R_gray = cv.cvtColor(image_R, cv.COLOR_BGR2GRAY) + 1e-1
    image_L_gray = cv.resize(image_L_gray,(int(image_L_gray.shape[1]/downscale),int(image_L_gray.shape[0]/downscale)),interpolation=cv.INTER_CUBIC)
    image_R_gray = cv.resize(image_R_gray,(int(image_R_gray.shape[1]/downscale),int(image_R_gray.shape[0]/downscale)),interpolation=cv.INTER_CUBIC)
    if(algor == 0): #OpenCV
        stereo = cv.StereoBM_create(numDisparities=16, blockSize=15)
        result = stereo.compute(image_L_gray,image_R_gray)
    elif(algor == 1): #Cost Block Matching
        result = vec_cost_block_matching(image_L_gray, image_R_gray, 9, 9, 16)
        disparity = result[0][:,:,0]
    elif(algor == 2): #Multiblock
        disparity = multiblock(image_L_gray, image_R_gray, 9, 9, 21, 3, 3, 21, 16)
    disparity = cv.resize(disparity,(disparity.shape[1]*downscale,disparity.shape[0]*downscale),interpolation=cv.INTER_CUBIC)
    cv.imshow('Disparity',disparity)
    cv.waitKey(5000)
    cv.destroyAllWindows()

if __name__ == "__main__":
    processCapture(0,2)
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