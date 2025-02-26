from AccelerometerGamepad import *
""" from inputs import get_gamepad

while 1:
  gamepad = get_gamepad()
  for event in gamepad:
    print(event.code) """


gamepad = AccelerometerGamepad()
gamepad.loopData()