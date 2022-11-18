#import RPi.GPIO as GPIO
from time import sleep 
from os import system
import cv2 as cv
import sys
#sys.path.insert(1,'/home/tdhl/Github/TheDoPro/Vision')
sys.path.insert(1,'../Vision')
import customStereo as cs 
import tkinter as tk
from PIL import Image, ImageTk

freq = 0.1

def setupGPIO(master):
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	for button in master['buttons']: 
		GPIO.setup(master['buttons'][button]['pin'],GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

def updateState(master): 
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
			updateState(master)
		else:
			return
	print("Turning Off")
	system('clear')
	GPIO.cleanup()
	#system('sudo shutdown -h now')
	exit()

# Simulated Off State 
def offState(master):
	print("Hold Power to Turn On")
	changeState = 0
	powerCounter = 3
	while not changeState:
		sleep(freq)
		updateState(master)
		powerCounter = powerCounter - 1 if master['buttons']['power']['state'] else 3 
		changeState = not powerCounter
	print('Succesfully Turned CV System On!')
	rightPreview(master)

def rightPreview(master,prev):
	if(prev != None):
		prev.destroy()
	print("Right Preview")
	root = tk.Tk()
	root.title('PictureThis! (Right Preview)')
	right = cv.cvtColor(cv.imread('../Images/right_piano.png'),cv.COLOR_BGR2RGB)
	imTk = ImageTk.PhotoImage(image=Image.fromarray(right))
	lbl = tk.Label(root,image=imTk)
	lbl.grid(row=1,column=1)
	tk.Button(root,text="Left Preview",font=("Courier",24),command=lambda:leftPreview(master,root)).grid(row=2,column=1)
	tk.Button(root,text="Capture",font=("Courier",24),command=lambda:capture(master,root)).grid(row=2,column=2)
	tk.Button(root,text="Settings",font=("Courier",24),command=lambda:configSettings(master,root)).grid(row=2,column=3)
	root.mainloop()

	# changeState = 0
	# while not changeState:
	# 	sleep(freq)
	# 	updateState(master)
	# 	checkPower(master)
	# 	settings.activateSettings(master['settings'])
	# 	cs.readRight()
	# 	changeState = master['buttons']['sel2']['state'] ^ master['buttons']['capture']['state'] 
	# if master['buttons']['sel2']['state']: 
	# 	cv.destroyAllWindows()
	# 	print('Change State to Left Preview')
	# 	leftPreview(master)
	# elif master['buttons']['capture']['state']:
	# 	cv.destroyAllWindows()
	# 	print('Change State to Capture')
	# 	capture(master)

def leftPreview(master,prev):
	if(prev != None):
		prev.destroy()
	print("Left Preview")
	root = tk.Tk()
	root.title('PictureThis! (Left Preview)')
	left = cv.cvtColor(cv.imread('../Images/left_piano.png'),cv.COLOR_BGR2RGB)
	imTk = ImageTk.PhotoImage(image=Image.fromarray(left))
	lbl = tk.Label(root,image=imTk)
	lbl.grid(row=1,column=1)
	tk.Button(root,text="Right Preview",font=("Courier",24),command=lambda:rightPreview(master,root)).grid(row=2,column=1)
	tk.Button(root,text="Capture",font=("Courier",24),command=lambda:capture(master,root)).grid(row=1,column=2)
	tk.Button(root,text="Settings",font=("Courier",24),command=lambda:configSettings(master['settings'],root)).grid(row=1,column=3)
	root.mainloop()
	# changeState = 0
	# while not changeState:
	# 	sleep(freq)
	# 	updateState(master)
	# 	checkPower(master)
	# 	settings.activateSettings(master['settings'])
	# 	cs.readLeft()
	# 	changeState = master['buttons']['sel1']['state'] ^ master['buttons']['capture']['state'] 
	# if master['buttons']['sel1']['state']: 
	# 	cv.destroyAllWindows()
	# 	print('Change State to Right Preview')
	# 	rightPreview(master)
		
	# elif master['buttons']['capture']['state']:
	# 	cv.destroyAllWindows()
	# 	print('Change State to Capture')
	# 	capture(master)

def capture(master,prev):
	if(prev != None):
		prev.destroy()
	print('Capturing')
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
	if(master['settings']['flash'] == 'On'):
		pass
		#turn on flash
	image_L = cv.imread('../Images/left_piano.png', 0)
	image_L = cv.cvtColor(image_L, cv.COLOR_BGR2RGB)
	image_R = cv.imread('../Images/right_piano.png', 0)
	image_R = cv.cvtColor(image_R, cv.COLOR_BGR2RGB)

	result = cs.processCapture(image_L,image_R,config[master['settings']['mode']]['algor'],config[master['settings']['mode']]['downscale'])
	#turn off flash
	
	# root = tk.Tk()
	# root.title('PictureThis! (Disparity)')
	# imTk = ImageTk.PhotoImage(image=Image.fromarray(result))
	# lbl = tk.Label(root,image=imTk)
	# lbl.pack()
	# root.after(3000,lambda:root.destroy())
	# root.mainloop()
	cv.imshow('result',result)
	cv.waitKey(3000)
	cv.destroyAllWindows()
	rightPreview(master,None)

def configSettings(master,prev):
	prev.destroy()
	cv.destroyAllWindows()
	root = tk.Tk()
	root.title('Settings')
	root.geometry('640x480')

	title = tk.Label(root,text='Settings',font=("Courier",30))
	title.grid(row=0,column=1)
	
	modeLabel = tk.Label(root,text="Disparity Mode: ",font=("Courier",24))
	modeLabel.grid(row=1,column=1)
	modes = ['OpenCV','Cost Block','Multiblock']
	mode = tk.StringVar(root)
	mode.set(master['settings']['mode'])
	modeSelection = tk.OptionMenu(root,mode,*modes)
	modeSelection.grid(row=1,column=2)

	rectLabel = tk.Label(root,text="Rectification: ",font=("Courier",24))
	rectLabel.grid(row=2,column=1)
	rectifications = ['On','Off']
	rectification = tk.StringVar(root)
	rectification.set(master['settings']['rectification'])
	rectSelection = tk.OptionMenu(root,rectification,*rectifications)
	rectSelection.grid(row=2,column=2)

	flashLabel = tk.Label(root,text="Flash: ",font=("Courier",24))
	flashLabel.grid(row=3,column=1)
	flashModes = ['On','Off']
	flash = tk.StringVar(root)
	flash.set(master['settings']['flash'])
	flashSelection = tk.OptionMenu(root,flash,*flashModes)
	flashSelection.grid(row=3,column=2)

	confirm = tk.Button(root,text="Update Settings",font=("Courier",24),command=lambda:updateSettings(master,mode.get(),rectification.get(),flash.get(),root))
	confirm.grid(row=4,column=2)
	
	root.mainloop()

def updateSettings(master,mode,rectification,flash,menu): 
	menu.destroy()
	master['settings']['mode'] = mode
	master['settings']['rectification'] = rectification
	master['settings']['flash'] = flash
	root = tk.Tk()
	root.title('Updated Settings: ')
	tk.Label(root,text="Updated Settings: ",font=("Courier",30)).pack()
	tk.Label(root,text=f"Disparity Mode: {master['settings']['mode']}",font=("Courier",24)).pack()
	tk.Label(root,text=f"Rectification: {master['settings']['rectification']}",font=("Courier",24)).pack()
	tk.Label(root,text=f"Flash: {master['settings']['flash']}",font=("Courier",24)).pack()
	root.after(3000,lambda:rightPreview(master,root))

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
			'mode': 'Cost Block',
			'rectification': 'Off',
			'flash': 'Off'
		}
	}

	#setupGPIO(master)
	#updateState(master)
	#offState(master)
	rightPreview(master,None)