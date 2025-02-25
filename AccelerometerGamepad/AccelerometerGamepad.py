from xdpchandler import *
import vgamepad as vg
import time
from InputProcessor import *
import threading
from PyQt6.QtCore import Qt, QRunnable, QThreadPool, pyqtSlot, pyqtSignal, QObject

class AccelerometerGamepad:
    def __init__(self):
        self.stop_event = threading.Event()
        self.xdpcHandler = self.initXdpcHandler()
        self.gamepad = vg.VX360Gamepad()
        self.joystickInputProcessor = TiltInputProcessor(self.gamepad, self.xdpcHandler)
        self.buttonInputProcessorA = ButtonInputProcessor(self.gamepad, self.xdpcHandler, vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        self.buttonInputProcessorB = ButtonInputProcessor(self.gamepad, self.xdpcHandler, vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
        self.inputProcessors = [self.joystickInputProcessor, self.buttonInputProcessorA, self.buttonInputProcessorB]


    def initXdpcHandler(self):
        xdpcHandler = XdpcHandler()

        if not xdpcHandler.initialize():
            xdpcHandler.cleanup()
            exit(-1)

        xdpcHandler.scanForDots()
        if len(xdpcHandler.detectedDots()) == 0:
            print("No Movella DOT device(s) found. Aborting.")
            xdpcHandler.cleanup()
            exit(-1)

        xdpcHandler.connectDots()

        if len(xdpcHandler.connectedDots()) == 0:
            print("Could not connect to any Movella DOT device(s). Aborting.")
            xdpcHandler.cleanup()
            exit(-1)

        for device in xdpcHandler.connectedDots():
            filterProfiles = device.getAvailableFilterProfiles()
            print("Available filter profiles:")
            for f in filterProfiles:
                print(f.label())

            print(f"Current profile: {device.onboardFilterProfile().label()}")
            if device.setOnboardFilterProfile("General"):
                print("Successfully set profile to General")
            else:
                print("Setting filter profile failed!")

            print("Setting quaternion CSV output")
            device.setLogOptions(movelladot_pc_sdk.XsLogOptions_Quaternion)

            print("Putting device into measurement mode.")
            if not device.startMeasurement(movelladot_pc_sdk.XsPayloadMode_ExtendedEuler):
                print(f"Could not put device into measurement mode. Reason: {device.lastResultText()}")
                continue

        return xdpcHandler

    def inputProcessorLoop(self, inputProcessor, deviceIndex):
        while not self.stop_event.is_set():
            if self.xdpcHandler.packetsAvailable():
                device = self.xdpcHandler.connectedDots()[deviceIndex]
                inputProcessor.processInput(device)

    def loopData(self):
        # First printing some headers so we see which data belongs to which device
        s = ""
        for device in self.xdpcHandler.connectedDots():
            s += f"{device.bluetoothAddress():42}"
        print("%s" % s, flush=True)

        # Create and start threads for input processors
        threads = []
        for i, inputProcessor in enumerate(self.inputProcessors):
            if self.xdpcHandler.connectedDots().__len__() <= i:
                break
            thread = threading.Thread(target=self.inputProcessorLoop, args=(inputProcessor, i))
            threads.append(thread)
            thread.start()

        try:
            while any(thread.is_alive() for thread in threads):
                for thread in threads:
                    thread.join(timeout=1)
        except KeyboardInterrupt:
            self.stop_event.set()
            for thread in threads:
                thread.join()

        print("\n-----------------------------------------", end="", flush=True)

        for device in self.xdpcHandler.connectedDots():
            print(f"\nResetting heading to default for device {device.portInfo().bluetoothAddress()}: ", end="", flush=True)
            if device.resetOrientation(movelladot_pc_sdk.XRM_DefaultAlignment):
                print("OK", end="", flush=True)
            else:
                print(f"NOK: {device.lastResultText()}", end="", flush=True)
        print("\n", end="", flush=True)

        print("\nStopping measurement...")
        for device in self.xdpcHandler.connectedDots():
            if not device.stopMeasurement():
                print("Failed to stop measurement.")
            if not device.disableLogging():
                print("Failed to disable logging.")

        self.xdpcHandler.cleanup()


    def setSens(self, xSens, ySens):
        for inputProcessor in self.inputProcessors:
            self.joystickInputProcessor.setSensitivity(xSens, ySens)
        

    def setThreshold(self, threshold):
        for inputProcessor in self.inputProcessors:
            inputProcessor.setThreshold(threshold)


    @pyqtSlot(float)
    def changeSensitivity(self, value):
        self.setSens(value,value)




