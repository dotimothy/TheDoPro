from time import sleep, localtime
import os
import cv2 as cv
import tkinter as tk
from PIL import Image, ImageTk
import sys

if(sys.platform == 'linux' or sys.platform == 'linux2'):
	import RPi.GPIO as GPIO
	sys.path.insert(1,'/home/tdlh/Github/TheDoPro/Vision')
else: 
	sys.path.insert(1,'../Vision')
programMode = 0

import customStereo as cs 

# GPIO Functions 

freq = 0.1

def setupGPIO(master):
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	for button in master['buttons']: 
		GPIO.setup(master['buttons'][button]['pin'],GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

def updateButtonState(master): 
	for button in master['buttons']: 
		master['buttons'][button]['state'] = GPIO.input(master['buttons'][button]['pin'])

def checkPower(master):
	powerCounter = 3250
	while(powerCounter > 0):
		sleep(0.001)
		if master['buttons']['power']['state']:
			if(powerCounter % 1000 == 0):
				print(int(powerCounter/1000))
			powerCounter = powerCounter - 1
			updateButtonState(master)
		else:
			return
	print("Turning Off")
	system('clear')
	GPIO.cleanup()
	#os.system('sudo shutdown -h now')
	exit()

# FSM Functions

# Main Window Function
def imagePreview(root,master,lbl):
	root.title(f'TheDoPro ({master["settings"]["state"]})')
	if(master['settings']['state'] == 'Right'):
		im = cs.readRight(programMode)
	elif(master['settings']['state'] == 'Left'):
		im = cs.readLeft(programMode)
	elif(master['settings']['state'] == 'Capture'):
		root.title(f'TheDoPro ({master["settings"]["state"]}: {master["settings"]["mode"]})')
		config = {'OpenCV': {
			'algor':0,
			'downscale':1
		},
		'Cost Block':{
			'algor':1,
			'downscale':4
		},
		'Multiblock':{
			'algor':2,
			'downscale':4
		}}
		image_L = cs.readLeft(programMode)
		image_R = cs.readRight(programMode)
		im = cs.processCapture(image_L,image_R,config[master['settings']['mode']]['algor'],config[master['settings']['mode']]['downscale'])
	if(master['settings']['save'] == 'On'):
		if(not os.path.exists('./results')):
			os.mkdir('./results')
		saveImage(im,'./results')
		master['settings']['save'] = 'Off'
	im = cv.resize(im,(640,480))
	imTk = ImageTk.PhotoImage(image=Image.fromarray(im))
	lbl.imtk = imTk
	lbl.configure(image=imTk)
	lbl.after(50,imagePreview,root,master,lbl)
	
def setupPreview(root,master,lbl):
	lbl.grid(row=1,column=1)
	tk.Button(root,text="Change Camera",font=("Courier",28),command=lambda:changeCamera(master)).grid(row=2,column=1)
	tk.Button(root,text="Save Image",font=("Courier",28),command=lambda:turnOnSave(master)).grid(row=1,column=2)
	tk.Button(root,text="Gallery",font=("Courier",28),command=lambda:openGallery('results')).grid(row=1,column=3)
	tk.Button(root,text="Capture",font=("Courier",28),command=lambda:updateState(master,'Capture')).grid(row=2,column=2)
	tk.Button(root,text="Settings",font=("Courier",28),command=lambda:configSettings(master)).grid(row=2,column=3)

def changeCamera(master):
	if(master['settings']['state'] == 'Right'):
		master['settings']['state'] = 'Left'
	else: 
		master['settings']['state'] = 'Right'
	print(f"Updated Window State to {master['settings']['state']}")

def turnOnSave(master):
	master['settings']['save'] = 'On'

def openGallery(directory):
	if(sys.platform == 'win32'):
		os.system(f'explorer {os.getcwd()}\\results')
	elif(sys.platform == 'linux' or sys.platform == 'linux2'):
		os.system(f'pcmanfm {os.getcwd()}/results')

def updateState(master,state):
	master['settings']['state'] = state
	print(f"Updated Window State to {master['settings']['state']}")

def saveImage(im,outputDir):
	current = localtime()
	outputPath = f'{outputDir}/{current.tm_mon}{current.tm_mday}{current.tm_year}_{current.tm_hour}_{current.tm_min}_{current.tm_sec}.jpg'
	cv.imwrite(outputPath,cv.cvtColor(im,cv.COLOR_RGB2BGR))
	root = tk.Tk()
	root.title('Saving')
	tk.Label(root,text=f'Saved Output to {outputPath}',font=("Courier",28)).pack()
	root.after(2000,root.destroy)

def configSettings(master):
	root = tk.Tk()
	root.title('Settings')
	root.geometry('960x540')

	title = tk.Label(root,text='Settings',font=("Courier",30))
	title.grid(row=0,column=1)
	
	modeLabel = tk.Label(root,text="Disparity Mode: ",font=("Courier",28))
	modeLabel.grid(row=1,column=1)
	modes = ['OpenCV','Cost Block','Multiblock']
	mode = tk.StringVar(root)
	mode.set(master['settings']['mode'])
	modeSelection = tk.OptionMenu(root,mode,*modes)
	modeSelection.grid(row=1,column=2)

	rectLabel = tk.Label(root,text="Rectification: ",font=("Courier",28))
	rectLabel.grid(row=2,column=1)
	rectifications = ['On','Off']
	rectification = tk.StringVar(root)
	rectification.set(master['settings']['rectification'])
	rectSelection = tk.OptionMenu(root,rectification,*rectifications)
	rectSelection.grid(row=2,column=2)

	flashLabel = tk.Label(root,text="Flash: ",font=("Courier",28))
	flashLabel.grid(row=3,column=1)
	flashModes = ['On','Off']
	flash = tk.StringVar(root)
	flash.set(master['settings']['flash'])
	flashSelection = tk.OptionMenu(root,flash,*flashModes)
	flashSelection.grid(row=3,column=2)

	confirm = tk.Button(root,text="Update Settings",font=("Courier",28),command=lambda:updateSettings(master,mode.get(),rectification.get(),flash.get(),root))
	confirm.grid(row=4,column=2)
	
	root.mainloop()

def updateSettings(master,mode,rectification,flash,menu):
	master['settings']['mode'] = mode
	master['settings']['rectification'] = rectification
	master['settings']['flash'] = flash
	menu.destroy()

# Test Driver
if __name__ == '__main__':
	# pins are physical
	master = {	
		'buttons': {
			'power': {'pin': 10},
			'capture':{'pin': 12}, 
			'sel1': {'pin': 16},
			'sel2': {'pin': 18}
		},
		'settings': {
			'state': 'Right',
			'mode': 'OpenCV',
			'rectification': 'Off',
			'flash': 'Off',
			'save': 'Off'
		}
	}

	#setupGPIO(master)
	#updateButtonState(master)
	#offState(master)
	root = tk.Tk()
	root.geometry('1280x720')
	lbl = tk.Label(root)
	im = None
	setupPreview(root,master,lbl)
	imagePreview(root,master,lbl)
	root.mainloop()
