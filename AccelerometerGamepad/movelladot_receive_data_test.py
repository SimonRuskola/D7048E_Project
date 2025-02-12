
from xdpchandler import *
import vgamepad as vg
import time

gamepad = vg.VX360Gamepad()

if __name__ == "__main__":
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


        # Enable logging to a file
        """ logFileName = "logfile_" + device.bluetoothAddress().replace(':', '-') + ".csv"
        print(f"Enable logging to: {logFileName}")
        if not device.enableLogging(logFileName):
            print(f"Failed to enable logging. Reason: {device.lastResultText()}") """

        print("Putting device into measurement mode.")
        if not device.startMeasurement(movelladot_pc_sdk.XsPayloadMode_ExtendedEuler):
            print(f"Could not put device into measurement mode. Reason: {device.lastResultText()}")
            continue

    print("\nMain loop. Recording data for 10 seconds.")
    print("-----------------------------------------")

    # First printing some headers so we see which data belongs to which device
    s = ""
    for device in xdpcHandler.connectedDots():
        s += f"{device.bluetoothAddress():42}"
    print("%s" % s, flush=True)

    orientationResetDone = False
    startTime = movelladot_pc_sdk.XsTimeStamp_nowMs()
    while True:
        if xdpcHandler.packetsAvailable():
            s = ""
            for device in xdpcHandler.connectedDots():
                # Retrieve a packet
                packet = xdpcHandler.getNextPacket(device.portInfo().bluetoothAddress())

                if packet.containsOrientation():
                    euler = packet.orientationEuler()
                    s += f"Roll:{euler.x():7.2f}, Pitch:{euler.y():7.2f}, Yaw:{euler.z():7.2f}| "

            
                if packet.containsFreeAcceleration():
                    acc = packet.freeAcceleration()
                    s += f"AccX:{acc[0]:7.2f}, AccY:{acc[2]:7.2f}, AccZ:{acc[1]:7.2f} | "
              

            print("%s\r" % s, end="", flush=True)

            if not orientationResetDone and movelladot_pc_sdk.XsTimeStamp_nowMs() - startTime > 5000:
                for device in xdpcHandler.connectedDots():
                    print(f"\nResetting heading for device {device.portInfo().bluetoothAddress()}: ", end="", flush=True)
                    if device.resetOrientation(movelladot_pc_sdk.XRM_Heading):
                        print("OK", end="", flush=True)
                    else:
                        print(f"NOK: {device.lastResultText()}", end="", flush=True)
                print("\n", end="", flush=True)
                orientationResetDone = True

            
            x_value = euler.x()/40
            y_value = euler.y()/20

            if x_value > 1:
                x_value = 1
            if (x_value < -1):
                x_value = -1
            
            if y_value > 1:
                y_value = 1
            if y_value < -1:
                y_value = -1


        

            """ x_value = acc[0]/10
            y_value = acc[2]/10 """

            gamepad.right_joystick_float(x_value_float=x_value, y_value_float=y_value)
            gamepad.update()
            gamepad.reset()

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
