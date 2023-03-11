import socket
import cv2
import numpy as np

# define the host and port number
HOST = 'localhost'
PORT = 1234

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to the server
s.connect((HOST, PORT))
print(f'Connected to {HOST}:{PORT}')

# load the images
img1 = cv2.imread('../Images/daniel_L.jpg', cv2.IMREAD_COLOR)
img2 = cv2.imread('../Images/daniel_R.jpg', cv2.IMREAD_COLOR)

# encode the images as raw bytes
img1_data = cv2.imencode('.jpg', img1)[1].tobytes()
img2_data = cv2.imencode('.jpg', img2)[1].tobytes()

# send the images to the server
s.sendall(len(img1_data).to_bytes(4, byteorder='big'))
s.sendall(img1_data)

s.sendall(len(img2_data).to_bytes(4, byteorder='big'))
s.sendall(img2_data)

# close the connection
s.close()
