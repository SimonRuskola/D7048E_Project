from abc import ABC, abstractmethod
import math
import vgamepad as vg
import time

class InputProcessor(ABC):
    def __init__(self, gamepad, xdpcHandler):
        self.gamepad = gamepad
        self.xdpcHandler = xdpcHandler
        # sensitivity for joystick axis, lower is more sensitive
        self.x_sens = 50
        self.y_sens = 10

        # threshold for button press
        self.hysteresis_threshold = 7 
        self.deadzone = 0.1  # Default deadzone value

    @abstractmethod
    def processInput(self, device):
        pass

    def updateRightJoystick(self, x_value, y_value): # todo maybe include deadzone
        # Apply deadzone
        if abs(x_value) < self.deadzone:
            x_value = 0
        if abs(y_value) < self.deadzone:
            y_value = 0

        if x_value > 1:
            x_value = 1
        if x_value < -1:
            x_value = -1

        if y_value > 1:
            y_value = 1
        if y_value < -1:
            y_value = -1

        self.gamepad.right_joystick_float(x_value_float=x_value, y_value_float=y_value)
        self.gamepad.update()

    def setThreshold(self, threshold):
        self.hysteresis_threshold = threshold

    def setSensitivity(self, x_sens, y_sens):
        self.x_sens = x_sens
        self.y_sens = y_sens   

    def setDeadzone(self, deadzone):
        self.deadzone = deadzone

class TiltInputProcessor(InputProcessor):
    def __init__(self, gamepad, xdpcHandler):
        super().__init__(gamepad, xdpcHandler)

      

    def processInput(self, device):
        packet = self.xdpcHandler.getNextPacket(device.portInfo().bluetoothAddress())
        s = ""

        if packet.containsOrientation():
            euler = packet.orientationEuler()
            s += f"Roll:{euler.x():7.2f}, Pitch:{euler.y():7.2f}, Yaw:{euler.z():7.2f}| "
        
        if packet.containsFreeAcceleration():
            acc = packet.freeAcceleration()
            s += f"AccX:{acc[0]:7.2f}, AccY:{acc[2]:7.2f}, AccZ:{acc[1]:7.2f} | "

        #print("%s\r" % s, end="", flush=True)
        
        x_value = euler.x() / self.x_sens
        y_value = euler.y() / self.y_sens

        self.updateRightJoystick(x_value, y_value)



class ButtonInputProcessor(InputProcessor):
    def __init__(self, gamepad, xdpcHandler, button):
        super().__init__(gamepad, xdpcHandler)
        self.filtered_acc = [0, 0, 0]
        self.alpha = 0.5  # Smoothing factor for low-pass filter
        self.hysteresis_buffer = 1  # Buffer to prevent spamming
        self.button_pressed = False
        self.last_press_time = 0
        self.debounce_time = 0.5  # 500 ms debounce time
        self.button = button  # Button to be pressed


    def low_pass_filter(self, acc): # not sure if this helps
        for i in range(3):
            self.filtered_acc[i] = self.alpha * acc[i] + (1 - self.alpha) * self.filtered_acc[i]
        return self.filtered_acc

    def processInput(self, device):
        packet = self.xdpcHandler.getNextPacket(device.portInfo().bluetoothAddress())
        s = ""

        if packet.containsFreeAcceleration():
            acc = packet.freeAcceleration()
            filtered_acc = self.low_pass_filter(acc)
            totalAcc = math.sqrt(sum(fa ** 2 for fa in filtered_acc))
            s += f"AccX:{filtered_acc[0]:7.2f}, AccY:{filtered_acc[2]:7.2f}, AccZ:{filtered_acc[1]:7.2f}, AccTot:{totalAcc:7.2f}  | "
        

        #print("%s\r" % s, end="", flush=True)

        current_time = time.time()
        if totalAcc > self.hysteresis_threshold and not self.button_pressed:
            if current_time - self.last_press_time > self.debounce_time:
                self.button_pressed = True
                self.last_press_time = current_time
                self.gamepad.press_button(button=self.button)
                self.gamepad.update()

        elif totalAcc < (self.hysteresis_threshold - self.hysteresis_buffer) and self.button_pressed:
            self.button_pressed = False
            self.gamepad.release_button(button=self.button)
            self.gamepad.update()













