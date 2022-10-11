from socket import *
import cv2 as cv

serverConfig = {'host': '0.0.0.0', 'port':1234}

serverSock = socket(AF_INET,SOCK_STREAM)