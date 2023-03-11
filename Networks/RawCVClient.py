import socket
import cv2 as cv
import numpy as np

# define the host and port number
HOST = 'localhost'
PORT = 1234



def sendStereoPair(imgL,imgR):
	# create a socket object
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# connect to the server
	s.connect((HOST, PORT))
	print(f'Connected to {HOST}:{PORT}')

	# encode the images as raw bytes
	imgL_data = cv.imencode('.jpg', imgL)[1].tobytes()
	imgR_data = cv.imencode('.jpg', imgR)[1].tobytes()

	# send the images to the server
	s.sendall(len(imgL_data).to_bytes(4, byteorder='big'))
	s.sendall(imgL_data)

	s.sendall(len(imgR_data).to_bytes(4, byteorder='big'))
	s.sendall(imgR_data)

	# close the connection
	s.close()

if __name__ == '__main__':
	# load the images
	imgL = cv.cvtColor(cv.imread('../Images/daniel_L.jpg', cv.IMREAD_COLOR),cv.COLOR_BGR2RGB)
	imgR = cv.cvtColor(cv.imread('../Images/daniel_R.jpg', cv.IMREAD_COLOR),cv.COLOR_BGR2RGB)
	sendStereoPair(imgL,imgR)