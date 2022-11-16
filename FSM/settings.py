import tkinter as tk
import cv2 as cv

def activateSettings(setting): 
	root = tk.Tk()
	root.title('Settings')
	tk.Button(root,text="Settings",font=("Courier",24),command=lambda:configSettings(setting,root)).pack()
	root.mainloop()


def configSettings(settings,act):
	act.destroy()
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
	mode.set(settings['mode'])
	modeSelection = tk.OptionMenu(root,mode,*modes)
	modeSelection.grid(row=1,column=2)

	rectLabel = tk.Label(root,text="Rectification: ",font=("Courier",24))
	rectLabel.grid(row=2,column=1)
	rectifications = ['On','Off']
	rectification = tk.StringVar(root)
	rectification.set(settings['rectification'])
	rectSelection = tk.OptionMenu(root,rectification,*rectifications)
	rectSelection.grid(row=2,column=2)

	confirm = tk.Button(root,text="Update Settings",font=("Courier",24),command=lambda:updateSettings(settings,mode.get(),rectification.get()))
	confirm.grid(row=3,column=2)



	root.mainloop()


def updateSettings(settings,mode,rectification): 
	settings['mode'] = mode
	settings['rectification'] = rectification
	print(f'Updated Mode to {settings["mode"]}')
	print(f'Updated Rectification to {settings["rectification"]}')


if __name__ == '__main__':
	setting = {'mode':'Efficiency','rectification':'On'}
	activateSettings(setting)
