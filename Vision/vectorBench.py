import PIL
import matplotlib.pyplot as plt
import cv2 as cv
import time
import numpy as np
from scipy import ndimage as nd

#Load Images
image_L = cv.imread('../Images/left_piano.png', 1)
image_L = cv.cvtColor(image_L, cv.COLOR_BGR2RGB)
image_R = cv.imread('../Images/right_piano.png', 1)
image_R = cv.cvtColor(image_R, cv.COLOR_BGR2RGB)

image_L_gray = cv.cvtColor(image_L, cv.COLOR_BGR2GRAY) + 1e-1
image_R_gray = cv.cvtColor(image_R, cv.COLOR_BGR2GRAY) + 1e-1

#Parameters
block_x = 9
block_y = 9
disp = 16

column_offset = np.floor(block_x/2).astype(int)
row_offset = np.floor(block_y/2).astype(int)

col_bound_L = column_offset + disp
col_bound_U = image_L_gray.shape[1] - column_offset
row_bound_L = row_offset
row_bound_U = image_L_gray.shape[0] - row_offset
rsize= row_bound_U - row_bound_L

cost = np.empty((row_bound_U-row_bound_L, col_bound_U-col_bound_L, disp))
cost_vec = cost

L_avg = nd.uniform_filter(image_L_gray, (block_y, block_x), mode='constant')
R_avg = nd.uniform_filter(image_R_gray, (block_y, block_x), mode='constant')


#Unvectorized
# start = time.time()
# for d in range(0, disp):
#     for r in range(row_bound_L, row_bound_U):
#         for c in range(col_bound_L, col_bound_U):

#             L_cost = (image_L_gray[r-row_offset:r+row_offset+1, c-column_offset:c+column_offset+1] - L_avg[r, c])
#             R_cost = (image_R_gray[r-row_offset:r+row_offset+1, c-column_offset-d:c+column_offset-d+1] - R_avg[r, c-d])

#             cost[r-row_bound_L, c-col_bound_L, d] = np.sum(L_cost*R_cost)/np.sqrt((np.sum(L_cost**2)*np.sum(R_cost**2)))
# end = time.time()
# print(f'Unvectorized: {end - start} seconds')

#Vectorized
start = time.time()
for d in range(0, disp):
  idx = (np.arange(row_bound_L, row_bound_U)*rsize + \
        np.arange(col_bound_L, col_bound_U).reshape(-1, 1)).transpose()
  bead = (np.arange(-row_offset, row_offset+1)*rsize + \
          np.arange(-column_offset, column_offset+1).reshape(-1, 1)).reshape(-1, 1)

  L_string = idx.flatten()
  R_string = (idx - d).flatten()
  L_braid  = L_string + bead
  R_braid  = L_string + bead

  L_cost_str = (image_L_gray - \
                L_avg).flatten()[L_braid.flatten()].reshape(L_braid.shape)
  R_cost_str = (image_R_gray - \
                R_avg).flatten()[R_braid.flatten()].reshape(R_braid.shape)
  LR_cost_str = L_cost_str*R_cost_str

  L_cost = L_cost_str.sum(axis=0).reshape(idx.shape)
  R_cost = R_cost_str.sum(axis=0).reshape(idx.shape)
  L_sqr_cost = (L_cost_str**2).sum(axis=0).reshape(idx.shape)
  R_sqr_cost = (R_cost_str**2).sum(axis=0).reshape(idx.shape)
  LR_cost = LR_cost_str.sum(axis=0).reshape(idx.shape)

  cost_vec[:, :, d] = LR_cost/np.sqrt(L_sqr_cost*R_sqr_cost)
end = time.time() 
print(f'Vectorized: {end - start} seconds')

# plt.figure(figsize=(20, 10))
# # plt.subplot(121)
# # plt.imshow(cost[:, :, 15], cmap='gray')
# # plt.subplot(122)
# plt.imshow(cost_vec[:, :, 15], cmap='gray')
# plt.savefig('result.png')