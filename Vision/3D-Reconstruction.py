# The Do-Pro 3D Scanning Pipeline
# Timothy Do, Daniel Jilani, Zaya Lazar, Harrison Nguyen

import open3d as o3d
import customStereo as cs
import numpy as np
import cv2 as cv
from time import sleep, localtime
import os
import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk
import sys
if(sys.platform == 'linux' or sys.platform == 'linux2'):
	import RPi.GPIO as GPIO

# Point Cloud Functions
def create_pcd(img, depth, f, cx, cy):
        rows, columns = depth.shape

        dy = np.arange(rows).reshape(-1, 1)*np.ones(columns)
        dx = np.arange(columns)*np.ones(rows).reshape(-1, 1)

        x = (dx - cx) * depth / f
        y = (dy - cy) * depth / f

        pcd = np.array([x.flatten(), y.flatten(), depth.flatten()]).transpose()
        pcdRGB = img.reshape(-1, 3)/255
        
        pcd_o3d = o3d.geometry.PointCloud()  
        pcd_o3d.points = o3d.utility.Vector3dVector(pcd)  
        pcd_o3d.colors = o3d.utility.Vector3dVector(pcdRGB) 
        
        return pcd_o3d

def createSTL(inputPCPath,outputSTLPath):
	# Load Point-Cloud file using Open3D
	pcd = o3d.io.read_point_cloud(inputPCPath)
	pcd.estimate_normals()

	# Reconstruct surface and convert to mesh
	mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd)
	mesh.compute_vertex_normals()

	# Convert to STL file
	o3d.io.write_triangle_mesh(outputSTLPath, mesh)

programMode = 2
if(programMode and not(cs.checkCams())):
	programMode = 2


# GPIO Functions 

def setupGPIO(master):
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	for button in master['buttons']: 
		GPIO.setup(master['buttons'][button]['pin'],GPIO.IN,pull_up_down=GPIO.PUD_UP)
	for led in master['leds']:
		GPIO.setup(master['leds'][led]['pin'],GPIO.OUT)

def updateButtonState(master): 
	for button in master['buttons']: 
		master['buttons'][button]['state'] = 0 if(GPIO.input(master['buttons'][button]['pin'])) else 1

def printButtonState(master):
	for button in master['buttons']:
		print(f"{button}: {master['buttons'][button]['state']}")
	print()


# FSM Functions


def imagePreview(root,master,lbl):
	im = []
	image_L = []
	image_R = []
	if(master['lastState'] != master['settings']['state']):
		setupPreview(root,master,lbl)
	if(sys.platform == 'linux' or sys.platform == 'linux2'):
		updateButtonState(master)
		if(master['buttons']['sel1']['state'] and not(master['buttons']['sel2']['state'])and not(master['buttons']['capture']['state'])): #Right
			updateState(master,'Right')
		elif(not(master['buttons']['sel1']['state']) and master['buttons']['sel2']['state'] and not(master['buttons']['capture']['state'])): #Left
			updateState(master,'Left')
		elif(not(master['buttons']['sel1']['state']) and not(master['buttons']['sel2']['state']) and master['buttons']['capture']['state']): #Capture
			updateState(master,'Capture')
		elif(master['buttons']['sel1']['state'] and master['buttons']['sel2']['state'] and not(master['buttons']['capture']['state'])): #Settings
			configSettings(master)
	root.title(f'TheDoPro 3D-Reconstruction Mode (State: {master["settings"]["state"]})')
	if(master['settings']['state'] == 'Right'):
		im = cs.readRight(programMode)
		if(master['settings']['rectification'] == 'On'):
			im = cs.rectifyRight(im)
		if(sys.platform == 'linux' or sys.platform == 'linux2'):
			GPIO.output(master['leds']['capture']['pin'],0)
			GPIO.output(master['leds']['flash']['pin'],0)
	elif(master['settings']['state'] == 'Left'):
		im = cs.readLeft(programMode)
		if(master['settings']['rectification'] == 'On'):
			im = cs.rectifyLeft(im)
		if(sys.platform == 'linux' or sys.platform == 'linux2'):
			GPIO.output(master['leds']['capture']['pin'],0)
			GPIO.output(master['leds']['flash']['pin'],0)
	elif(master['settings']['state'] == 'Capture'):
		if(sys.platform == 'linux' or sys.platform == 'linux2'):
			GPIO.output(master['leds']['capture']['pin'],1)
			if(master['settings']['flash'] == 'On'):
				GPIO.output(master['leds']['flash']['pin'],1)
			else: 
				GPIO.output(master['leds']['flash']['pin'],0)
		root.title(f'TheDoPro 3D-Reconstruction Mode (State: {master["settings"]["state"]}: {master["settings"]["mode"]})')
		image_L = cs.readLeft(programMode)
		image_R = cs.readRight(programMode)
		if(master['settings']['rectification'] == 'On'):
			image_L = cs.rectifyLeft(image_L)
			image_R = cs.rectifyRight(image_R)
		im = image_L
		pcd = create_pcd(image_L,-cs.disparityToDepthScanning(cs.stereoSGBM.compute(image_L,image_R)),f=551.038915543398,cx=287.359515629467,cy=269.784821130991)
		if(sys.platform == 'win32'):
			o3d.visualization.draw_geometries([pcd], point_show_normal=True)
		updateState(master,'Right')
	if(master['settings']['save'] == 'On'):
		if(not os.path.exists('./results')):
			os.mkdir('./results')
		saveImage(im,'./results')
		if(master['settings']['state'] == 'Capture'):
			saveImage(image_L,'./results')
			saveImage(image_R,'./results')
		master['settings']['save'] = 'Off'
	im = cv.resize(im,(640,480))
	imTk = ImageTk.PhotoImage(image=Image.fromarray(im))
	lbl.imtk = imTk
	lbl.configure(image=imTk)
	master['lastState'] =  master['settings']['state']
	lbl.after(25,imagePreview,root,master,lbl)
	
def setupPreview(root,master,lbl):
	if(sys.platform == 'win32'):
		root.iconbitmap('../Images/favicon.ico')
	for widget in root.winfo_children():
		if isinstance(widget,tk.Button):
			widget.destroy()
	lbl.grid(row=1,column=1)
	if(master['settings']['state'] != 'Capture'):
		tk.Button(root,text="Change Camera",font=("Courier",28),command=lambda:changeCamera(master)).grid(row=2,column=1,padx=10,pady=10)
	else:
		tk.Button(root,text="Revert",font=("Courier",28),command=lambda:changeCamera(master)).grid(row=2,column=1,padx=10,pady=10)
	tk.Button(root,text="Save Image",font=("Courier",28),command=lambda:turnOnSave(master)).grid(row=1,column=2,padx=10,pady=10)
	tk.Button(root,text="Gallery",font=("Courier",28),command=lambda:openGallery('results')).grid(row=1,column=3,padx=10,pady=10)
	tk.Button(root,text="Scan",font=("Courier",28),command=lambda:updateState(master,'Capture')).grid(row=2,column=2,padx=10,pady=10)
	tk.Button(root,text="Settings",font=("Courier",28),command=lambda:configSettings(master)).grid(row=2,column=3,padx=10,pady=10)
	if(programMode == 1):
		tk.Button(root,text="Correct",font=("Courier",28),command=lambda:cs.correctPosition()).grid(row=3,column=3,padx=10,pady=10)

def updateState(master,state):
	master['settings']['state'] = state
	print(f"Updated Window State to {master['settings']['state']}")

def changeCamera(master):
	if(master['settings']['state'] == 'Right'):
		updateState(master,'Left')
	else: 
		master['settings']['state'] = 'Right'
		updateState(master,'Right')

def turnOnSave(master):
	master['settings']['save'] = 'On'

def openGallery(directory):
	if(sys.platform == 'win32'):
		os.system(f'explorer {os.getcwd()}\\results')
	elif(sys.platform == 'linux' or sys.platform == 'linux2'):
		os.system(f'pcmanfm {os.getcwd()}/results')


def saveImage(im,outputDir):
	current = localtime()
	outputPath = f'{outputDir}/{current.tm_mon}{current.tm_mday}{current.tm_year}_{current.tm_hour}_{current.tm_min}_{current.tm_sec}.jpg'
	dup = 1
	while(os.path.exists(outputPath)):
		outputPath = f'{outputDir}/{current.tm_mon}{current.tm_mday}{current.tm_year}_{current.tm_hour}_{current.tm_min}_{current.tm_sec}_{str(dup)}.jpg'
		dup = dup + 1
	cv.imwrite(outputPath,cv.cvtColor(im,cv.COLOR_RGB2BGR))
	root = tk.Tk()
	root.title('Saving')
	tk.Label(root,text=f'Saved Output to {outputPath}',font=("Courier",28)).pack()
	root.after(2000,root.destroy)

def configSettings(master):
	root = tk.Tk()
	if(sys.platform == 'win32'): 
		root.iconbitmap('../Images/favicon.ico')
	root.title('Settings')
	root.geometry('960x540')

	title = tk.Label(root,text='Settings',font=("Courier",30))
	title.grid(row=0,column=1)

	rectLabel = tk.Label(root,text="Rectification: ",font=("Courier",28))
	rectLabel.grid(row=2,column=1)
	rectifications = ['On','Off']
	rectification = tk.StringVar(root)
	rectification.set(master['settings']['rectification'])
	rectSelection = tk.OptionMenu(root,rectification,*rectifications)
	rectSelection.config(font=tkFont.Font(family='Arial',size=24,weight=tkFont.BOLD))
	rectSelections = root.nametowidget(rectSelection.menuname)
	rectSelections.configure(font=tkFont.Font(family='Arial',size=18,weight=tkFont.BOLD))
	rectSelection.grid(row=2,column=2)


	disparity = tk.StringVar(root)
	disparity.set(master['settings']['disparity'])
	if(master['settings']['mode'] == 'OpenCV_SGBM' or master['settings']['mode'] == 'OpenCV_BM'):
		disLabel = tk.Label(root,text="Disparity Range: ",font=("Courier",28))
		disLabel.grid(row=4,column=1)
		disModes = [16,32,64,128,256]
		disSelection = tk.OptionMenu(root,disparity,*disModes)
		disSelection.config(font=tkFont.Font(family='Arial',size=24,weight=tkFont.BOLD))
		disSelections = root.nametowidget(disSelection.menuname)
		disSelections.configure(font=tkFont.Font(family='Arial',size=18,weight=tkFont.BOLD))
		disSelection.grid(row=4,column=2)

	flash = tk.StringVar(root)
	flash.set(master['settings']['flash'])
	if(programMode == 1 and sys.platform == 'linux'):
		flashLabel = tk.Label(root,text="Flash: ",font=("Courier",28))
		flashLabel.grid(row=6,column=1)
		flashModes = ['On','Off']
		flashSelection = tk.OptionMenu(root,flash,*flashModes)
		flashSelection.config(font=tkFont.Font(family='Arial',size=24,weight=tkFont.BOLD))
		flashSelections = root.nametowidget(flashSelection.menuname)
		flashSelections.configure(font=tkFont.Font(family='Arial',size=18,weight=tkFont.BOLD))
		flashSelection.grid(row=6,column=2)

	exposure = tk.StringVar(root)
	exposure.set(master['settings']['exposure'])
	if(programMode == 1):
		exposLabel = tk.Label(root,text="Exposure: ",font=("Courier",28))
		exposLabel.grid(row=7,column=1)
		exposModes = [-1.0,-2.0,-3.0,-4.0,-5.0,-6.0,-7.0,-8.0,-10.0,-11.0,-12.0,-13.0,-14.0]
		exposSelection = tk.OptionMenu(root,exposure,*exposModes)
		exposSelection.config(font=tkFont.Font(family='Arial',size=24,weight=tkFont.BOLD))
		exposSelections = root.nametowidget(exposSelection.menuname)
		exposSelections.configure(font=tkFont.Font(family='Arial',size=18,weight=tkFont.BOLD))
		exposSelection.grid(row=7,column=2)

	confirm = tk.Button(root,text="Update Settings",font=("Courier",28),command=lambda:updateSettings(master,rectification.get(),disparity.get(),flash.get(),exposure.get(),root))
	confirm.grid(row=8,column=2)
	
	root.mainloop()

def updateSettings(master,rectification,disp,flash,exposure,menu):
	master['settings']['rectification'] = rectification
	master['settings']['flash'] = flash
	master['settings']['disparity'] = int(disp)
	master['settings']['exposure'] = float(exposure)
	if(programMode == 1):
		cs.adjustExposure(master['settings']['exposure'])
	cs.adjustNumDisp(master['settings']['disparity'])
	menu.destroy()


if __name__ == '__main__':
	# f = 551.038915543398
	# cx = 287.359515629467
	# cy = 269.784821130991
	# image_L = cv.imread("../Images/cup_L.jpg")
	# image_L_gray = cv.cvtColor(image_L, cv.COLOR_BGR2GRAY)
	# image_L = cv.cvtColor(image_L, cv.COLOR_BGR2RGB)

	# image_R = cv.imread("../Images/cup_R.jpg")
	# image_R_gray = cv.cvtColor(image_L, cv.COLOR_BGR2GRAY)
	# image_R = cv.cvtColor(image_R, cv.COLOR_BGR2RGB)

	# cs.adjustNumDisp(256)
	# disparity = cs.stereoSGBM.compute(image_L, image_R)
	# depth =  -cs.disparityToDepthScanning(disparity)

	# pcd = create_pcd(image_L, depth, f, cx, cy)
	# o3d.visualization.draw_geometries([pcd], point_show_normal=True)

	# pins are physical
	master = {	
		'lastState': 'Right',
		'buttons': {
			'power': {'pin': 5},
			'capture':{'pin': 31}, 
			'sel1': {'pin': 11},
			'sel2': {'pin': 13}
		},
		'leds': {
			'flash': {'pin': 15},
			'capture':{'pin': 7}
		},
		'settings': {
			'state': 'Right',
			'mode': 'OpenCV_SGBM',
			'rectification': 'Off',
			'flash': 'Off',
			'save': 'Off',
			'disparity':64,
			'exposure':-6.0
		}
	}
	

	if(sys.platform == 'linux' or sys.platform == 'linux2'):
		setupGPIO(master)
	root = tk.Tk()
	root.geometry('1280x720')
	lbl = tk.Label(root)
	im = None
	setupPreview(root,master,lbl)
	imagePreview(root,master,lbl)
	cs.adjustExposure(master['settings']['exposure'])
	cs.adjustNumDisp(master['settings']['disparity'])
	root.mainloop()
	if(sys.platform == 'linux' or sys.platform == 'linux2'):
		GPIO.cleanup()