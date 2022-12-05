import cv2
import time
import os

cap = cv2.VideoCapture(2) #left 
cap2 = cv2.VideoCapture(1) #right

num = 0

if(not os.path.exists('./left') and not os.path.exists('./right')):
    os.mkdir('./left')
    os.mkdir('./right')

while cap.isOpened() and num < 5:

    succes1, img = cap.read()
    succes2, img2 = cap2.read()

    cv2.imwrite('./left/imageL' + str(num) + '.png', img)
    cv2.imwrite('./right/imageR' + str(num) + '.png', img2)

    num = num + 1

    cv2.imshow('Img 1',img)
    cv2.imshow('Img 2',img2)

    cv2.waitKey(1)
    time.sleep(1)

# Release and destroy all windows before termination
cap.release()
cap2.release()

cv2.destroyAllWindows()
