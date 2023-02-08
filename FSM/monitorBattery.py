import time
import csv
import datetime

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008


# Software SPI configuration:
CLK  = 21
MISO = 19
MOSI = 20
CS   = 16
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)


print('Monitoring Voltage of the Battery using MCP3008')
power = True
csvFile = open('voltage.csv','w')
writer = csv.writer(csvFile)
writer.writerow(['Timestamp','Raw','Voltage'])
csvFile.close()
while power:
    raw = mcp.read_adc(0)
    voltage =  round((5.18/1024)*raw,4)
    ts = datetime.datetime.now()
    # Print the ADC values.
    print(f'{ts}: Raw: {raw}, Voltage: {voltage} V')
    csvFile = open('voltage.csv','a')
    writer = csv.writer(csvFile)
    writer.writerow([str(ts),str(raw),str(voltage)])
    csvFile.close()
    #if(voltage < 3.3):
        #power = False
        #print('Out of Power')
    # Pause
    time.sleep(5)
