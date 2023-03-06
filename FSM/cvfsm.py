from time import sleep, localtime
import os
import cv2 as cv
import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk
import sys

if(sys.platform == 'linux' or sys.platform == 'linux2'):
	import RPi.GPIO as GPIO
	sys.path.insert(1,'/home/tdlh/Github/TheDoPro/Vision')
else: 
	sys.path.insert(1,'../Vision')
programMode = 1


import customStereo as cs 
if(programMode and not(cs.checkCams())):
	programMode = 0


# GPIO Functions 

freq = 0.1

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
	root.title(f'TheDoPro ({master["settings"]["state"]})')
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
		root.title(f'TheDoPro ({master["settings"]["state"]}: {master["settings"]["mode"]})')
		config = {'OpenCV_BM': {
			'algor':0,
			'downscale':1
		},
		'OpenCV_SGBM': {
			'algor':1,
			'downscale':1
		},
		'Cost Block':{
			'algor':2,
			'downscale':4
		},
		'Multiblock':{
			'algor':3,
			'downscale':8
		}}
		image_L = cs.readLeft(programMode)
		image_R = cs.readRight(programMode)
		if(master['settings']['rectification'] == 'On'):
			image_L = cs.rectifyLeft(image_L)
			image_R = cs.rectifyRight(image_R)
		re = master['settings']['relative'] == 'On' 
		im = cs.processCapture(image_L,image_R,config[master['settings']['mode']]['algor'],config[master['settings']['mode']]['downscale'],re,master['settings']['colormap'])
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
		tk.Button(root,text="Change Camera",font=("Courier",28),command=lambda:changeCamera(master)).grid(row=2,column=1)
	else:
		tk.Button(root,text="Revert",font=("Courier",28),command=lambda:changeCamera(master)).grid(row=2,column=1)
	tk.Button(root,text="Save Image",font=("Courier",28),command=lambda:turnOnSave(master)).grid(row=1,column=2)
	tk.Button(root,text="Gallery",font=("Courier",28),command=lambda:openGallery('results')).grid(row=1,column=3)
	tk.Button(root,text="Capture",font=("Courier",28),command=lambda:updateState(master,'Capture')).grid(row=2,column=2)
	tk.Button(root,text="Settings",font=("Courier",28),command=lambda:configSettings(master)).grid(row=2,column=3)
	if(programMode == 1):
		tk.Button(root,text="Correct",font=("Courier",28),command=lambda:cs.correctPosition()).grid(row=3,column=3)

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
	
	modeLabel = tk.Label(root,text="Disparity Mode: ",font=("Courier",28))
	modeLabel.grid(row=1,column=1)
	modes = ['OpenCV_BM','OpenCV_SGBM','Cost Block','Multiblock']
	mode = tk.StringVar(root)
	mode.set(master['settings']['mode'])
	modeSelection = tk.OptionMenu(root,mode,*modes)
	modeSelection.config(font=tkFont.Font(family='Arial',size=24,weight=tkFont.BOLD))
	modeSelections = root.nametowidget(modeSelection.menuname)
	modeSelections.configure(font=tkFont.Font(family='Arial',size=18,weight=tkFont.BOLD))
	modeSelection.grid(row=1,column=2)

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

	cmapLabel = tk.Label(root,text="Color Map: ",font=("Courier",28))
	cmapLabel.grid(row=3,column=1)
	cmapModes = ['Jet','Gray','Bone','Rainbow','HSV','Viridis']
	cmap = tk.StringVar(root)
	cmap.set(master['settings']['colormap'].capitalize())
	cmapSelection = tk.OptionMenu(root,cmap,*cmapModes)
	cmapSelection.config(font=tkFont.Font(family='Arial',size=24,weight=tkFont.BOLD))
	cmapSelections = root.nametowidget(cmapSelection.menuname)
	cmapSelections.configure(font=tkFont.Font(family='Arial',size=18,weight=tkFont.BOLD))
	cmapSelection.grid(row=3,column=2)

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

	relative = tk.StringVar(root)
	relative.set(master['settings']['relative'])
	if(master['settings']['mode'] == 'OpenCV_SGBM' or master['settings']['mode'] == 'OpenCV_BM'):
		reLabel = tk.Label(root,text="Relative: ",font=("Courier",28))
		reLabel.grid(row=5,column=1)
		reModes = ['On','Off']
		reSelection = tk.OptionMenu(root,relative,*reModes)
		reSelection.config(font=tkFont.Font(family='Arial',size=24,weight=tkFont.BOLD))
		reSelections = root.nametowidget(reSelection.menuname)
		reSelections.configure(font=tkFont.Font(family='Arial',size=18,weight=tkFont.BOLD))
		reSelection.grid(row=5,column=2)

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

	confirm = tk.Button(root,text="Update Settings",font=("Courier",28),command=lambda:updateSettings(master,mode.get(),rectification.get(),cmap.get(),disparity.get(),relative.get(),flash.get(),exposure.get(),root))
	confirm.grid(row=8,column=2)
	
	root.mainloop()

def updateSettings(master,mode,rectification,cmap,disp,relative,flash,exposure,menu):
	master['settings']['mode'] = mode
	master['settings']['rectification'] = rectification
	master['settings']['flash'] = flash
	master['settings']['relative'] = relative
	master['settings']['colormap'] = cmap.lower()
	master['settings']['disparity'] = int(disp)
	master['settings']['exposure'] = float(exposure)
	if(programMode == 1):
		cs.adjustExposure(master['settings']['exposure'])
	cs.adjustNumDisp(master['settings']['disparity'])
	menu.destroy()

# Test Driver
if __name__ == '__main__':
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
			'relative':'Off',
			'colormap':'jet',
			'disparity':64,
			'exposure':-6.0
		}
	}

	#setupGPIO(master)
	#updateButtonState(master)
	#offState(master)
	

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
	# while True:
	# 	sleep(1)
	# 	updateButtonState(master)
	# 	printButtonState(master)
