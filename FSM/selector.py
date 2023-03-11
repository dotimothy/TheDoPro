import os
import sys
import tkinter as tk
from PIL import Image, ImageTk

def setupGPIO(master):
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	for button in master['buttons']: 
		GPIO.setup(master['buttons'][button]['pin'],GPIO.IN,pull_up_down=GPIO.PUD_UP)

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

def setupPreview(root,lbl,exit):
	root.title('TheDoPro Program Selector')
	root.geometry('240x320')
	if(sys.platform == 'win32'):
		root.iconbitmap('../Images/favicon.ico')
	lbl.grid(row=1,column=1,padx=10,pady=10)
	#imTk = ImageTk.PhotoImage(image=Image.open('../Images/TheDoPro.jpg'))
	#lbl.imtk = imTk
	#lbl.configure(image=imTk)
	tk.Button(root,text="Visualiziation",font=("Courier",28),command=lambda:triggerProgram('vis',root)).grid(row=2,column=1,padx=10,pady=10)
	tk.Button(root,text="ADAS-Detection",font=("Courier",28),command=lambda:triggerProgram('ADAS',root)).grid(row=3,column=1,padx=10,pady=10)
	tk.Button(root,text="3D-Scanning",font=("Courier",28),command=lambda:triggerProgram('3D',root)).grid(row=2,column=2,padx=10,pady=10)
	tk.Button(root,text="Shutdown",font=("Courier",28),command=lambda:shutdown()).grid(row=3,column=2,padx=10,pady=10)


if __name__ == '__main__':
	while True: 
		root = tk.Tk()
		lbl = tk.Label(root)
		setupPreview(root,lbl,exit)
		root.mainloop()