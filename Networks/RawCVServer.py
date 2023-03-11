import socket
import cv2
import numpy as np
import sys
sys.path.insert(1,'/home/tdlh/Github/TheDoPro/Vision')

# define the host and port number
HOST = 'localhost'
PORT = 1234

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to a public host and port
s.bind((HOST, PORT))

# listen for incoming connections
s.listen()
try: 
	while True:
		# wait for a connection
		conn, addr = s.accept()
		print(f'Connected by {addr}')

		# receive the first image
		img_size = int.from_bytes(conn.recv(4), byteorder='big')
		img_data = b''
		while len(img_data) < img_size:
		    data = conn.recv(min(1024, img_size - len(img_data)))
		    if not data:
		        break
		    img_data += data
		img1 = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)

		# receive the second image
		img_size = int.from_bytes(conn.recv(4), byteorder='big')
		img_data = b''
		while len(img_data) < img_size:
		    data = conn.recv(min(1024, img_size - len(img_data)))
		    if not data:
		        break
		    img_data += data
		img2 = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)

		# show the images
		cv2.imshow('image1', img1)
		cv2.imshow('image2', img2)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

		# close the connection
		conn.close()
except KeyboardInterrupt:
	s.close()
