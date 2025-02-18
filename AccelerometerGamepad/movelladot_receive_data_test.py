from xdpchandler import *
import vgamepad as vg
import time
from InputProcessor import TiltInputProcessor, InputProcessor, AccelerationInputProcessor, PositionInputProcessor

def initXdpcHandler():
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


def loopData(xdpcHandler, inputProcessor):
    print("\nMain loop. Recording data for 10 seconds.")
    print("-----------------------------------------")

    # First printing some headers so we see which data belongs to which device
    s = ""
    for device in xdpcHandler.connectedDots():
        s += f"{device.bluetoothAddress():42}"
    print("%s" % s, flush=True)

    #startTime = movelladot_pc_sdk.XsTimeStamp_nowMs()
    while True:
        if xdpcHandler.packetsAvailable():
            s = ""
            for device in xdpcHandler.connectedDots():
                # Retrieve a packet
                inputProcessor.processInput(device)

    print("\n-----------------------------------------", end="", flush=True)

    for device in xdpcHandler.connectedDots():
        print(f"\nResetting heading to default for device {device.portInfo().bluetoothAddress()}: ", end="", flush=True)
        if device.resetOrientation(movelladot_pc_sdk.XRM_DefaultAlignment):
            print("OK", end="", flush=True)
        else:
            print(f"NOK: {device.lastResultText()}", end="", flush=True)
    print("\n", end="", flush=True)

    print("\nStopping measurement...")
    for device in xdpcHandler.connectedDots():
        if not device.stopMeasurement():
            print("Failed to stop measurement.")
        if not device.disableLogging():
            print("Failed to disable logging.")

    xdpcHandler.cleanup()

def recieveData():
    xdpcHandler = initXdpcHandler()
    gamepad = vg.VX360Gamepad()
    inputProcessor = TiltInputProcessor(gamepad,xdpcHandler)
    #inputProcessor = AccelerationInputProcessor(gamepad, xdpcHandler)
    #inputProcessor = PositionInputProcessor(gamepad, xdpcHandler)
    loopData(xdpcHandler, inputProcessor)

if __name__ == "__main__":
    recieveData()




