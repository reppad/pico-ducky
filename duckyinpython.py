# License : GPLv2.0
# copyright (c) 2021  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)

import usb_hid
from adafruit_hid.keyboard import Keyboard

# comment out these lines for non_US keyboards
#from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
#from adafruit_hid.keycode import Keycode

# uncomment these lines for non_US keyboards
# replace LANG with appropriate language
from keyboard_layout_win_fr import KeyboardLayout
from keycode_win_fr import Keycode

import supervisor

import time
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
from microcontroller import pin
import pwmio

led = pwmio.PWMOut(pin.GPIO25, frequency=5000, duty_cycle=0)

def led_pwm_up(led, callback=None):
    for i in range(100):
        # PWM LED up and down
        if i < 50:
            led.duty_cycle = int(i * 2 * 65535 / 100)  # Up
        if callback is not None:
            callback()
        time.sleep(0.01)
def led_pwm_down(led, callback=None):
    for i in range(100):
        # PWM LED up and down
        if i >= 50:
            led.duty_cycle = 65535 - int((i - 50) * 2 * 65535 / 100)  # Down
        if callback is not None:
            callback()
        time.sleep(0.01)

duckyCommands = {
    'WINDOWS': Keycode.WINDOWS, 'GUI': Keycode.GUI,
    'APP': Keycode.APPLICATION, 'MENU': Keycode.APPLICATION, 'SHIFT': Keycode.SHIFT,
    'ALT': Keycode.ALT, 'CONTROL': Keycode.CONTROL, 'CTRL': Keycode.CONTROL,
    'DOWNARROW': Keycode.DOWN_ARROW, 'DOWN': Keycode.DOWN_ARROW, 'LEFTARROW': Keycode.LEFT_ARROW,
    'LEFT': Keycode.LEFT_ARROW, 'RIGHTARROW': Keycode.RIGHT_ARROW, 'RIGHT': Keycode.RIGHT_ARROW,
    'UPARROW': Keycode.UP_ARROW, 'UP': Keycode.UP_ARROW, 'BREAK': Keycode.PAUSE,
    'PAUSE': Keycode.PAUSE, 'CAPSLOCK': Keycode.CAPS_LOCK, 'DELETE': Keycode.DELETE,
    'END': Keycode.END, 'ESC': Keycode.ESCAPE, 'ESCAPE': Keycode.ESCAPE, 'HOME': Keycode.HOME,
    'INSERT': Keycode.INSERT, 'NUMLOCK': Keycode.KEYPAD_NUMLOCK, 'PAGEUP': Keycode.PAGE_UP,
    'PAGEDOWN': Keycode.PAGE_DOWN, 'PRINTSCREEN': Keycode.PRINT_SCREEN, 'ENTER': Keycode.ENTER,
    'SCROLLLOCK': Keycode.SCROLL_LOCK, 'SPACE': Keycode.SPACE, 'TAB': Keycode.TAB,
    'BACKSPACE': Keycode.BACKSPACE,
    'A': Keycode.A, 'B': Keycode.B, 'C': Keycode.C, 'D': Keycode.D, 'E': Keycode.E,
    'F': Keycode.F, 'G': Keycode.G, 'H': Keycode.H, 'I': Keycode.I, 'J': Keycode.J,
    'K': Keycode.K, 'L': Keycode.L, 'M': Keycode.M, 'N': Keycode.N, 'O': Keycode.O,
    'P': Keycode.P, 'Q': Keycode.Q, 'R': Keycode.R, 'S': Keycode.S, 'T': Keycode.T,
    'U': Keycode.U, 'V': Keycode.V, 'W': Keycode.W, 'X': Keycode.X, 'Y': Keycode.Y,
    'Z': Keycode.Z, 'F1': Keycode.F1, 'F2': Keycode.F2, 'F3': Keycode.F3,
    'F4': Keycode.F4, 'F5': Keycode.F5, 'F6': Keycode.F6, 'F7': Keycode.F7,
    'F8': Keycode.F8, 'F9': Keycode.F9, 'F10': Keycode.F10, 'F11': Keycode.F11,
    'F12': Keycode.F12,

}
def convertLine(line):
    newline = []
    # print(line)
    # loop on each key - the filter removes empty values
    for key in filter(None, line.split(" ")):
        key = key.upper()
        # find the keycode for the command in the list
        command_keycode = duckyCommands.get(key, None)
        if command_keycode is not None:
            # if it exists in the list, use it
            newline.append(command_keycode)
        elif hasattr(Keycode, key):
            # if it's in the Keycode module, use it (allows any valid keycode)
            newline.append(getattr(Keycode, key))
        else:
            # if it's not a known key name, show the error for diagnosis
            print(f"Unknown key: <{key}>")
    # print(newline)
    return newline

def runScriptLine(line):
    for k in line:
        kbd.press(k)
    kbd.release_all()

def sendString(line):
    layout.write(line)

def parseLine(line):
    global defaultDelay
    if(line[0:3] == "REM"):
        # ignore ducky script comments
        pass
    elif(line[0:5] == "DELAY"):
        time.sleep(float(line[6:])/1000)
    elif(line[0:6] == "STRING"):
        sendString(line[7:])
    elif(line[0:5] == "PRINT"):
        print("[SCRIPT]: " + line[6:])
    elif(line[0:6] == "IMPORT"):
        runScript(line[7:])
    elif(line[0:13] == "DEFAULT_DELAY"):
        defaultDelay = int(line[14:]) * 10
    elif(line[0:12] == "DEFAULTDELAY"):
        defaultDelay = int(line[13:]) * 10
    elif(line[0:3] == "LED"):
        if(led.value == True):
            led.value = False
        else:
            led.value = True
    else:
        newScriptLine = convertLine(line)
        runScriptLine(newScriptLine)

kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)

# turn off automatically reloading when files are written to the pico
supervisor.disable_autoreload()

# sleep at the start to allow the device to be recognized by the host computer
time.sleep(.5)

led_pwm_up(led)

#init button
runScriptButton_pin = DigitalInOut(pin.GPIO23) # WeAct RP2040 button
runScriptButton_pin.switch_to_input()
runScriptButton = Debouncer(runScriptButton_pin)

def getProgrammingStatus():
    '''
    # check pin.GPIO0 for setup mode
    # see setup mode for instructions
    progStatusPin = DigitalInOut(pin.GPIO0)
    progStatusPin.switch_to_input(pull=Pull.UP)
    progStatus = not progStatusPin.value
    '''
    progStatus = runScriptButton_pin.value # using WeAct RP2040 button to set programming mode also
    return(progStatus)


defaultDelay = 0

def runScript(file):
    global defaultDelay

    duckyScriptPath = file
    try:
        f = open(duckyScriptPath,"r",encoding='utf-8')
        previousLine = ""
        for line in f:
            line = line.rstrip()
            if(line[0:6] == "REPEAT"):
                for i in range(int(line[7:])):
                    #repeat the last command
                    parseLine(previousLine)
                    time.sleep(float(defaultDelay)/1000)
            else:
                parseLine(line)
                previousLine = line
            time.sleep(float(defaultDelay)/1000)
    except OSError as e:
        print("Unable to open file ", file)

def selectPayload():
    payload = "payload.dd"
    # check switch status
    # payload1 = pin.GPIOIO4 to GND
    # payload2 = pin.GPIOIO5 to GND
    # payload3 = pin.GPIOIO10 to GND
    # payload4 = pin.GPIOIO11 to GND
    payload1Pin = DigitalInOut(pin.GPIO4)
    payload1Pin.switch_to_input(pull=Pull.UP)
    payload1State = not payload1Pin.value
    payload2Pin = DigitalInOut(pin.GPIO5)
    payload2Pin.switch_to_input(pull=Pull.UP)
    payload2State = not payload2Pin.value
    payload3Pin = DigitalInOut(pin.GPIO10)
    payload3Pin.switch_to_input(pull=Pull.UP)
    payload3State = not payload3Pin.value
    payload4Pin = DigitalInOut(pin.GPIO11)
    payload4Pin.switch_to_input(pull=Pull.UP)
    payload4State = not payload4Pin.value


    if(payload1State == True):
        payload = "payload.dd"

    elif(payload2State == True):
        payload = "payload2.dd"

    elif(payload3State == True):
        payload = "payload3.dd"

    elif(payload4State == True):
        payload = "payload4.dd"

    else:
        # if all pins are high, then no switch is present
        # default to payload1
        payload = "payload.dd"

    return payload

def checkRunScriptButton() :
    global runScriptButton, payload
    runScriptButton.update()
    if(runScriptButton.rose):
        runScript(payload)
        runScriptButtonPushed = False


progStatus = False
progStatus = getProgrammingStatus()
payload = selectPayload()

if(progStatus == False):
    # not in setup mode, inject the payload
    print("Running ", payload)
    runScript(payload)

    print("Done")
else:
    print("Update your payload")

while True:
    led_pwm_up(led, checkRunScriptButton)
    led_pwm_down(led, checkRunScriptButton)
