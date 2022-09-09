from microcontroller import pin
from digitalio import DigitalInOut
import storage

noStorageStatus = False
noStoragePin = DigitalInOut(pin.GPIO23) # WeAct RP2040 button
noStoragePin.switch_to_input()
noStorageStatus = not noStoragePin.value

if(noStorageStatus == True):
    # don't show USB drive to host PC
    storage.disable_usb_drive()
    print("Disabling USB drive")
else:
    # normal boot
    print("USB drive enabled")
