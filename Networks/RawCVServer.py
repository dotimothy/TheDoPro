import socket
import cv2 as cv
import numpy as np
import sys
import open3d as o3d
sys.path.insert(1,'../Vision')
threed = __import__('3D-Reconstruction')


# define the host and port number
HOST = 'localhost'
PORT = 1234

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to a public host and port
s.bind((HOST, PORT))

# listen for incoming connections
s.listen()
while True:
	try: 
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
		imgL = cv.imdecode(np.frombuffer(img_data, np.uint8), cv.IMREAD_COLOR)

		# receive the second image
		img_size = int.from_bytes(conn.recv(4), byteorder='big')
		img_data = b''
		while len(img_data) < img_size:
		    data = conn.recv(min(1024, img_size - len(img_data)))
		    if not data:
		        break
		    img_data += data
		imgR = cv.imdecode(np.frombuffer(img_data, np.uint8), cv.IMREAD_COLOR)

		pcd = threed.reconstructPointCloudFromDisp(imgL,imgR)
		o3d.visualization.draw_geometries([pcd], point_show_normal=True)


		# close the connection
		conn.close()
	except KeyboardInterrupt:
		s.close()
		exit()
