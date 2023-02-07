import cv2

leftCam = cv2.VideoCapture(2)
#leftCam.open('/dev/v4l/by-id/usb-Arducam_Technology_Co.__Ltd._USB_2.0_camera_SN0001-video-index0')
rightCam = cv2.VideoCapture(1)
#rightCam.open('/dev/v4l/by-id/usb-Arducam_Technology_Co.__Ltd._USB_2.0_camera_SN0001-video-index1')

#leftCam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#leftCam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
#rightCam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#rightCam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

while True:
    leftCheck, leftFrame = leftCam.read()
    rightCheck, rightFrame = rightCam.read()
    cv2.imshow('left', leftFrame)
    cv2.imshow('right',rightFrame)

    key = cv2.waitKey(1)
    if key == 27:
        break

leftCam.release()
rightCam.release()
cv2.destroyAllWindows()