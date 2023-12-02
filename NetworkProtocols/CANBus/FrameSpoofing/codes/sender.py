# Sender
# initialize CAN controler
from time import sleep
from rp2 import *
c = CAN()

frame = CANFrame(CANID(0x123), data=b'AA')
for _ in range(1, 10):
    c.send_frame(frame)
    sleep(1)
