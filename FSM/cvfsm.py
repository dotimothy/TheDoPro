import RPi.GPIO as GPIO
from time import sleep 
from os import system
import cv2 as cv
import sys
sys.path.insert(1,'/home/tdlh/Github/TheDoPro/Vision')
import customStereo as cs 

freq = 0.1

def setupGPIO(buttons):
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	for button in buttons: 
		GPIO.setup(buttons[button]['pin'],GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

def updateState(buttons): 
	for button in buttons: 
		buttons[button]['state'] = GPIO.input(buttons[button]['pin'])

def checkPower(buttons):
	powerCounter = 3250
	while(powerCounter > 0):
		sleep(0.001)
		if buttons['power']['state']:
			if(powerCounter % 1000 == 0):
				print(int(powerCounter/1000))
			powerCounter = powerCounter - 1
			updateState(buttons)
		else:
			return
	print("Turning Off")
	system('clear')
	GPIO.cleanup()
	exit()

def settings(buttons):
	changeState = 0 
	while not changeState:
		changeState = 1
	rightPreview(buttons)
	

def offState(buttons):
	print("Hold Power to Turn On")
	changeState = 0
	powerCounter = 3
	while not changeState:
		sleep(freq)
		updateState(buttons)
		powerCounter = powerCounter - 1 if buttons['power']['state'] else 3 
		changeState = not powerCounter
	print('Succesfully Turned CV System On!')
	rightPreview(buttons)

def rightPreview(buttons):
	print("Right Preview")
	changeState = 0
	while not changeState:
		sleep(freq)
		updateState(buttons)
		checkPower(buttons)
		cs.readRight()
		changeState = buttons['sel2']['state'] ^ buttons['capture']['state'] 
	if buttons['sel2']['state']: 
		cv.destroyAllWindows()
		print('Change State to Left Preview')
		leftPreview(buttons)
		
	elif buttons['capture']['state']:
		cv.destroyAllWindows()
		print('Change State to Capture')
		capture(buttons)

def leftPreview(buttons):
	print("Left Preview")
	changeState = 0
	while not changeState:
		sleep(freq)
		updateState(buttons)
		checkPower(buttons)
		cs.readLeft()
		changeState = buttons['sel1']['state'] ^ buttons['capture']['state'] 
	if buttons['sel1']['state']: 
		cv.destroyAllWindows()
		print('Change State to Right Preview')
		rightPreview(buttons)
		
	elif buttons['capture']['state']:
		cv.destroyAllWindows()
		print('Change State to Capture')
		capture(buttons)

def capture(buttons):
	print('Capturing')
	cs.processCapture(1,4)
	rightPreview(buttons)

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
			'brightness': 50
		}
	}

	setupGPIO(master['buttons'])
	updateState(master['buttons'])
	offState(master['buttons'])
