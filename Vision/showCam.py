import cv2

leftCam = cv2.VideoCapture(2)
rightCam = cv2.VideoCapture(1)

while True:
    leftCheck, leftFrame = leftCam.read()
    rightCheck, rightFrame = rightCam.read()
    cv2.imshow('left', leftFrame)
    cv2.imshow('right',rightFrame)

    key = cv2.waitKey(1)
    if key == 27:
        break

cam.release()
cv2.destroyAllWindows()