import customStereo as cs
import time 

start = time.time() 
cs.processCapture(0,8)
print(f'Completed in {time.time() - 5 - start} s')

