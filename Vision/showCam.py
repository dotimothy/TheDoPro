import cv2 as cv

leftCam = cv.VideoCapture(0,cv.CAP_DSHOW)
#leftCam.open('/dev/v4l/by-id/usb-Arducam_Technology_Co.__Ltd._USB_2.0_camera_SN0001-video-index0')
rightCam = cv.VideoCapture(1,cv.CAP_DSHOW)
#rightCam.open('/dev/v4l/by-id/usb-Arducam_Technology_Co.__Ltd._USB_2.0_camera_SN0001-video-index1')
leftCam.set(cv.CAP_PROP_SETTINGS,1)
rightCam.set(cv.CAP_PROP_SETTINGS,1)

#leftCam.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
#leftCam.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
#rightCam.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
#rightCam.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)

while True:
    leftCheck, leftFrame = leftCam.read()
    rightCheck, rightFrame = rightCam.read()
    cv.imshow('left', leftFrame)
    cv.imshow('right',rightFrame)

    key = cv.waitKey(1)
    if key == 27:
        break

leftCam.release()
rightCam.release()
cv.destroyAllWindows()