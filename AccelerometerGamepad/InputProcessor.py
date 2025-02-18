from abc import ABC, abstractmethod

class InputProcessor(ABC):
    def __init__(self, gamepad, xdpcHandler):
        self.gamepad = gamepad
        self.xdpcHandler = xdpcHandler

    @abstractmethod
    def processInput(self, device):
        pass

    def updateJoystick(self, x_value, y_value):
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

        print("%s\r" % s, end="", flush=True)
        
        x_sens = 40
        y_sens = 20

        x_value = euler.x() / x_sens
        y_value = euler.y() / y_sens

        self.updateJoystick(x_value, y_value)

class AccelerationInputProcessor(InputProcessor):
    def __init__(self, gamepad, xdpcHandler):
        super().__init__(gamepad, xdpcHandler)

    def processInput(self, device):
        packet = self.xdpcHandler.getNextPacket(device.portInfo().bluetoothAddress())
        s = ""

        if packet.containsFreeAcceleration():
            acc = packet.freeAcceleration()
            s += f"AccX:{acc[0]:7.2f}, AccY:{acc[2]:7.2f}, AccZ:{acc[1]:7.2f} | "
        
        print("%s\r" % s, end="", flush=True)
        
        x_sens = 1.0
        y_sens = 1.0

        x_value = acc[0] / x_sens
        y_value = acc[1] / y_sens

        self.updateJoystick(x_value, y_value)

class PositionInputProcessor(InputProcessor):
    def __init__(self, gamepad, xdpcHandler):
        super().__init__(gamepad, xdpcHandler)
        self.position = [0, 0, 0]
        self.velocity = [0, 0, 0]
        self.last_time = None

    def processInput(self, device):
        import time
        packet = self.xdpcHandler.getNextPacket(device.portInfo().bluetoothAddress())
        
        if self.last_time is None:
            self.last_time = time.time()
            return

        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        s = ""

        if packet.containsFreeAcceleration():
            acc = packet.freeAcceleration()
            s += f"AccX:{acc[0]:7.2f}, AccY:{acc[2]:7.2f}, AccZ:{acc[1]:7.2f} | "
            
            for i in range(3):
                self.velocity[i] += acc[i] * dt
                self.position[i] += self.velocity[i] * dt

        print("%s\r" % s, end="", flush=True)
        
        x_sens = 1.0
        y_sens = 1.0

        x_value = self.position[0] / x_sens
        y_value = self.position[1] / y_sens

        self.updateJoystick(x_value, y_value)

