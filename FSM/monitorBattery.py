from time import sleep, localtime
import csv
import datetime

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import RPi.GPIO as GPIO
from tkinter import messagebox


# Software SPI configuration:
CLK  = 21
MISO = 19
MOSI = 20
CS   = 16
sleep = 5
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
GPIO.setup(3,GPIO.IN,pull_up_down=GPIO.PUD_UP)
threshold = 3.1
supply = 5.18

print('Monitoring Voltage of the Battery using MCP3008')
power = True
current = localtime()
fileName = f'voltage_{current.tm_mon}{current.tm_mday}_{current.tm_year}_{current.tm_hour}_{current.tm_min}_{current.tm_sec}.csv'
csvFile = open(fileName,'w')
writer = csv.writer(csvFile)
writer.writerow(['Timestamp','Raw','Voltage'])
csvFile.close()
while power:
    raw = mcp.read_adc(0)
    voltage =  round((supply/1024)*raw,4)
    ts = datetime.datetime.now()
    # Print the ADC values.
    print(f'{ts}: Raw: {raw}, Voltage: {voltage} V')
    csvFile = open(fileName,'a')
    writer = csv.writer(csvFile)
    writer.writerow([str(ts),str(raw),str(voltage)])
    csvFile.close()
    if(voltage < threshold):
        power = False
        messagebox.showwarning("Shut Down","Sleeping")
        time.sleep(30)
        os.system('sudo shutdown -h now')
    
    # Pause
    time.sleep(60)
