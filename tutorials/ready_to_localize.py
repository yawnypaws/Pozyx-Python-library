#!/usr/bin/env python
"""
ready_to_localize.py - Tutorial intended to show how to perform positioning with Pozyx.

It is planned to make a tutorial on the Pozyx site as well just like there is now
one for the Arduino, but their operation is very similar.
You can find the Arduino tutorial here:
    https://www.pozyx.io/Documentation/Tutorials/ready_to_localize
"""
from time import sleep
from pypozyx import *

port = '/dev/ttyACM0'

manual_calibration = True
remote = True
remote_id = 0x1000
if not remote:
    remote_id = None
# necessary data for calibration
num_anchors = 4
anchor_ids = [0x605D, 0x2000, 0x6044, 0x6639]
heights = [1920, 2025, 1330, 1510]
# manual calibration
anchors_x = [0, -10, 3999, 4060]
anchors_y = [0, 3950, 0, 3945]
# for 2.5D
height = 1000


class ReadyToLocalize():
    """Continuously calls the Pozyx positioning function and prints its position."""

    def __init__(self, port):
        try:
            self.pozyx = PozyxSerial(port)
        except:
            print('ERROR: Unable to connect to Pozyx, wrong port')
            raise SystemExit

        self.setup()
        while True:
            self.loop()

    def setup(self):
        """Sets up the Pozyx for positioning by calibrating its anchor list."""
        print("------------POZYX POSITIONING V1.0 - -----------\nNOTES: \n- No parameters required.\n\n- System will auto start calibration\n\n- System will auto start positioning\n- -----------POZYX POSITIONING V1.0 ------------\nSTART Ranging: ")
        # Adds
        self.pozyx.clearDevices()
        if manual_calibration:
            self.setAnchorsManual()
        else:
            status = self.pozyx.doAnchorCalibration(
                POZYX_2_5D, 30, anchor_ids, heights)
            if status == POZYX_FAILURE:
                # If automatic calibration fails, please use manual calibration
                # for now.
                print("ERROR: calibration\nReset required.")
                raise SystemExit
        self.printCalibrationResult()

    def loop(self):
        """Performs positioning and prints the results."""
        position = Coordinates()
        status = self.pozyx.doPositioning(
            position, POZYX_2_5D, height, remote_id=remote_id)
        if status == POZYX_SUCCESS:
            self.printCoordinates(position)

    def printCoordinates(self, pos):
        """Prints the coordinates in a human-readable way."""
        print("x(mm): {pos.x}, y(mm): {pos.y}, z(mm): {pos.z}".format(pos=pos))

    def setAnchorsManual(self):
        """Adds the manually measured anchors to the Pozyx's device list one for one."""
        for i in range(num_anchors):
            anchor_coordinates = Coordinates(
                anchors_x[i], anchors_y[i], heights[i])
            anchor = DeviceCoordinates(anchor_ids[i], 0x1, anchor_coordinates)
            status = self.pozyx.addDevice(anchor, remote_id)

    def printCalibrationResult(self):
        """Prints the anchor calibration results in a human-readable way."""
        list_size = SingleRegister()

        status = self.pozyx.getDeviceListSize(list_size, remote_id)
        print("List size: {0}".format(list_size[0]))
        if list_size[0] == 0:
            print("Calibration failed.\n%s" % self.pozyx.getSystemError())
            return
        device_list = DeviceList(list_size=list_size[0])
        status = self.pozyx.getDeviceIds(device_list, remote_id)
        print("Calibration result:")
        print("Anchors found: {0}".format(list_size[0]))
        print("Anchor IDs: ", device_list)

        for i in range(list_size[0]):
            anchor = Coordinates()
            status = self.pozyx.getDeviceCoordinates(
                device_list[i], anchor, remote_id)
            print("ANCHOR,0x%0.4x,%s" % (device_list[i], str(anchor)))

if __name__ == "__main__":
    r = ReadyToLocalize(port)
