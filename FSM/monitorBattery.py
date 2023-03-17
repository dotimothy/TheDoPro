from time import sleep, localtime
import csv
import datetime

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import RPi.GPIO as GPIO
import tkinter as tk


# Software SPI configuration:
CLK  = 21
MISO = 19
MOSI = 20
CS   = 16
powerBCM = 3
powerBoard = 5
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
# GPIO.setmode(GPIO.BCM)
GPIO.setup(powerBCM,GPIO.IN,pull_up_down=GPIO.PUD_UP)
threshold = 3.2
supply = 5.18

print('Monitoring Voltage of the Battery using MCP3008')
power = True
current = localtime()
fileName = f'voltage_{current.tm_mon}_{current.tm_mday}_{current.tm_year}_{current.tm_hour}_{current.tm_min}_{current.tm_sec}.csv'
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
    if(voltage < threshold or GPIO.input(powerBCM) == 0):
        power = False
        win = tk.Tk()
        msg = tk.Label(win,text="Shutting Down")
        msg.pack()
        win.mainloop()
        sleep(3)
        win.destroy()
        sleep(7)
        os.system('shutdown -h now')
    
    # Pause
    sleep(3)
