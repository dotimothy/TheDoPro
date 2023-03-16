import os
import sys
import tkinter as tk
from PIL import Image, ImageTk
import cv2 as cv
if(sys.platform == 'linux'):
	import RPi.GPIO as GPIO

def setupGPIO(master):
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	for button in master['buttons']: 
		GPIO.setup(master['buttons'][button]['pin'],GPIO.IN,pull_up_down=GPIO.PUD_UP)

def updateButtonState(master): 
	for button in master['buttons']: 
		master['buttons'][button]['state'] = 0 if(GPIO.input(master['buttons'][button]['pin'])) else 1

def triggerProgram(program,root):
	programs = {
		'vis':'cvfsm.py',
		'ADAS':'../Vision/ADAS.py',
		'3D':'../Vision/3D-Reconstruction.py'
	}
	root.destroy()
	os.system(f'python {programs[program]}')	

def shutdown():
	if(sys.platform == 'linux'):
		os.system('sudo shutdown now')
	else:
		os.system('cls')
	exit()

def setupPreview(root,lbl,master):
	if(master['setup'] == False):
		root.title('TheDoPro Program Selector')
		root.geometry('640x480')
		if(sys.platform == 'win32'):
			root.iconbitmap('../Images/favicon.ico')
		lbl.grid(row=1,column=1,padx=20,pady=10)
		im = cv.resize(cv.imread('../Images/TheDoPro.jpg'),(160,120))
		imTk = ImageTk.PhotoImage(image=Image.fromarray(im))
		lbl.imtk = imTk
		lbl.configure(image=imTk)
		tk.Button(root,text="Visualiziation",font=("Courier",16),command=lambda:triggerProgram('vis',root)).grid(row=2,column=1,padx=10,pady=10)
		tk.Button(root,text="ADAS-Detection",font=("Courier",16),command=lambda:triggerProgram('ADAS',root)).grid(row=3,column=1,padx=10,pady=10)
		tk.Button(root,text="3D-Scanning",font=("Courier",16),command=lambda:triggerProgram('3D',root)).grid(row=2,column=2,padx=10,pady=10)
		tk.Button(root,text="Shutdown",font=("Courier",16),command=lambda:shutdown()).grid(row=3,column=2,padx=10,pady=10)
		master['setup'] == True
	if(sys.platform == 'linux'):
		updateButtonState(master)
		if(master['buttons']['sel1']['state'] and not(master['buttons']['sel2']['state'])and not(master['buttons']['capture']['state'])): #Visualization
			triggerProgram('vis',root)
		elif(not(master['buttons']['sel1']['state']) and master['buttons']['sel2']['state'] and not(master['buttons']['capture']['state'])): #ADAS
			triggerProgram('ADAS',root)
		elif(not(master['buttons']['sel1']['state']) and not(master['buttons']['sel2']['state']) and master['buttons']['capture']['state']): #3D-Reconstruction
			triggerProgram('3D',root)
	root.after(100,setupPreview,root,lbl,master)


if __name__ == '__main__':
	master = {
		'buttons': {
			'power': {'pin': 5},
			'capture':{'pin': 31}, 
			'sel1': {'pin': 11},
			'sel2': {'pin': 13}
		},
		'setup':False
	}
	if(sys.platform == 'linux'):
		setupGPIO(master)
	while True: 
		root = tk.Tk()
		lbl = tk.Label(root)
		setupPreview(root,lbl,master)
		root.mainloop()