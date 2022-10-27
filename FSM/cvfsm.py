import RPi.GPIO as GPIO
from time import sleep 
from os import system

freq = 0.01

def setupGPIO(buttons):
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	for button in buttons: 
		GPIO.setup(buttons[button]['pin'],GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

def updateState(buttons): 
	for button in buttons: 
		buttons[button]['state'] = GPIO.input(buttons[button]['pin'])

def checkPower(buttons):
	powerCounter = 3000
	while(powerCounter > 0):
		sleep(freq/10)
		if buttons['power']['state']:
			powerCounter = powerCounter - 1
		else:
			return
	print("Turning Off")
	system('clear')
	GPIO.cleanup()
	exit()

def checkSettings(buttons):
	return buttons['sel1']['state'] & buttons['sel2']['state']

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
		if(checkSettings(buttons)):
			settings(buttons)
			continue
		changeState = buttons['sel2']['state'] ^ buttons['capture']['state'] 
	if buttons['sel2']['state']: 
		print('Change State to Left Preview')
		leftPreview(buttons)
	elif buttons['capture']['state']:
		print('Change State to Capture')
		capture(buttons)

def leftPreview(buttons):
	print("Left Preview")
	changeState = 0
	while not changeState:
		sleep(freq)
		updateState(buttons)
		checkPower(buttons)
		if(checkSettings(buttons)):
			settings(buttons)
			continue
		changeState = buttons['sel1']['state'] ^ buttons['capture']['state'] 
	if buttons['sel1']['state']: 
		print('Change State to Right Preview')
		rightPreview(buttons)
	elif buttons['capture']['state']:
		print('Change State to Capture')
		capture(buttons)

def capture(buttons):
	print('Capturing')
	sleep(2)
	checkPower(buttons)
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
