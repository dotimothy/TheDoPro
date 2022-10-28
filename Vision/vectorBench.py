import customStereo as cs
import time 

scale = 1
while(scale <= 16):
  start = time.time() 
  cs.processCapture(0,scale)
  print(f'Completed in {time.time() - 5 - start} s (downscale = {scale})')
  scale = scale * 2

