import tkinter as tk

def settings(settings):
	root = tk.Tk()
	root.title('Settings')
	root.geometry('640x480')

	title = tk.Label(root,text='Settings',font=("Courier",30))
	title.grid(row=0,column=1)
	
	modeLabel = tk.Label(root,text="Disparity Mode: ",font=("Courier",24))
	modeLabel.grid(row=1,column=1)
	modes = ['Efficiency','Quality']
	mode = tk.StringVar(root)
	mode.set(settings['mode'])
	modeSelection = tk.OptionMenu(root,mode,*modes)
	modeSelection.grid(row=1,column=2)

	confirm = tk.Button(root,text="Update Settings",font=("Courier",24),command=lambda:updateSettings(settings,mode.get()))
	confirm.grid(row=2,column=2)



	root.mainloop()


def updateSettings(settings,mode): 
	settings['mode'] = mode
	print(f'Updated Mode to {settings["mode"]}')


if __name__ == '__main__':
	setting = {'mode':'Efficiency'}
	settings(setting)
