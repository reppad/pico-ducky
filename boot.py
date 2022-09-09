from microcontroller import pin
import digitalio
import storage

noStorageStatus = False
noStoragePin = digitalio.DigitalInOut(pin.GPIO23) # WeAct RP2040 button
noStoragePin.switch_to_input(pull=digitalio.Pull.UP)
noStorageStatus = not noStoragePin.value

if(noStorageStatus == True):
    # don't show USB drive to host PC
    storage.disable_usb_drive()
    print("Disabling USB drive")
else:
    # normal boot
    print("USB drive enabled")
