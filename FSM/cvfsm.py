import RPi.GPIO as GPIO
from time import sleep 
from os import system
import cv2 as cv
import sys
sys.path.insert(1,'/home/tdhl/Github/TheDoPro/Vision')
import customStereo as cs 
import settings as settings

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

def rightPreview(master):
	print("Right Preview")
	changeState = 0
	while not changeState:
		sleep(freq)
		updateState(master)
		checkPower(master)
		cs.readRight()
		changeState = master['buttons']['sel2']['state'] ^ master['buttons']['capture']['state'] 
	if master['buttons']['sel2']['state']: 
		cv.destroyAllWindows()
		print('Change State to Left Preview')
		leftPreview(master)
		
	elif master['buttons']['capture']['state']:
		cv.destroyAllWindows()
		print('Change State to Capture')
		capture(master)

def leftPreview(master):
	print("Left Preview")
	changeState = 0
	while not changeState:
		sleep(freq)
		updateState(master)
		checkPower(master)
		cs.readLeft()
		changeState = master['buttons']['sel1']['state'] ^ master['buttons']['capture']['state'] 
	if master['buttons']['sel1']['state']: 
		cv.destroyAllWindows()
		print('Change State to Right Preview')
		rightPreview(master)
		
	elif master['buttons']['capture']['state']:
		cv.destroyAllWindows()
		print('Change State to Capture')
		capture(master)

def capture(master):
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
	image_L = cv.imread('../Images/left_piano.png', 1)
	image_L = cv.cvtColor(image_L, cv.COLOR_BGR2RGB)
	image_R = cv.imread('../Images/right_piano.png', 1)
	image_R = cv.cvtColor(image_R, cv.COLOR_BGR2RGB)

	image_L_gray = cv.cvtColor(image_L, cv.COLOR_BGR2GRAY) 
	image_R_gray = cv.cvtColor(image_R, cv.COLOR_BGR2GRAY) 
	cs.processCapture(image_L_gray,image_R_grayconfig[master['settings']['mode']]['algor'],config[master['settings']['mode']]['downscale'])
	rightPreview(master)

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
			'rectification': 'Off'
		}
	}

	setupGPIO(master)
	updateState(master)
	offState(master)
