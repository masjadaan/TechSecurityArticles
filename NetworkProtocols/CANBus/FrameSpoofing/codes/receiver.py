# Receiver
# initialize CAN controler
from rp2 import *
c = CAN()

# continuously monitoring CAN bus
while True: 
	frame = c.recv()
	if len(frame) > 0:
		print(frame)
