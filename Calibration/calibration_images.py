import cv2
import time

cap = cv2.VideoCapture(1)
cap2 = cv2.VideoCapture(2)

num = 0

while cap.isOpened() and num < 20:

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
