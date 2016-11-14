#!/usr/bin/env python
"""set_same_settings.py - sets all wanted devices on the same settings as the tag.

This script discovers all the devices in the environment and sets the UWB settings
of the devices whose IDs match the included ones.

It can also save to flash if so desired.
"""
from pypozyx import *
from pypozyx.definitions.registers import POZYX_UWB_CHANNEL, POZYX_UWB_RATES, POZYX_UWB_PLEN, POZYX_UWB_GAIN

save_to_flash = True
channel = 2
bitrate = 2  # 6.81 Mb/s
prf = 2  # 64MHz
plen = 0x04  # 64
gain = 15.0  # dummy value since can't be saved
uwb_settings = UWBSettings(channel, bitrate, prf, plen, gain)

devices = [0x6054, 0x6049, 0x604A]

port = 'COM12'


class SetSameUWBSettings:
    """Goes through the process of setting all IDs on same UWB settings"""

    def __init__(self, port, uwb_settings, devices, save_to_flash=False, max_consecutive_fails=10):
        self.uwb_settings = uwb_settings
        self.pozyx = PozyxSerial(port)
        self.devices = devices
        self.encountered = []

        self.save_to_flash = save_to_flash

        # refactor and work in:
        self.max_fails = max_consecutive_fails

        # move this to outside or keep it inside?
        self.discover_and_change()

    def discover_and_change(self):
        """Goes over every possible UWB configuration, performs discovery and then changes the UWB settings if necessary"""
        channels = [1, 2, 3, 4, 5, 7]
        bitrates = [0, 1, 2]
        prfs = [1, 2]
        plens = [0x04, 0x14, 0x24, 0x34, 0x08, 0x18, 0x28, 0x0C]
        for channel in channels:
            for bitrate in bitrates:
                for prf in prfs:
                    for plen in plens:
                        self.pozyx.clearDevices()
                        fails = 0
                        uwb_settings = UWBSettings(
                            channel, bitrate, prf, plen, 15.0)
                        self.pozyx.setUWBSettings(uwb_settings)
                        # will continue when UWB settings have been correctly
                        # set
                        while not self.pozyx.setUWBSettings(uwb_settings):
                            print("Not able to set UWB settings %s on local device" % str(
                                self.uwb_settings))
                            fails += 1
                            if fails == self.max_fails:
                                print("Skipping this settings")
                                break
                        uwb_check = UWBSettings()
                        self.pozyx.getUWBSettings(uwb_check)
                        print("Set UWB settings %s on local device" %
                              str(uwb_check))
                        self.change_settings(self.discover_devices())
        # reset the UWB settings of the local tag to the necessary one
        while not self.pozyx.setUWBSettings(self.uwb_settings):
            print("Not able to set UWB settings %s on local device" %
                  str(self.uwb_settings))
        if save_to_flash:
            self.save_settings()
        print('DONE!')

    def discover_devices(self):
        """Discovers UWB settings """
        self.pozyx.doDiscovery()
        list_size = SingleRegister()
        while not self.pozyx.getDeviceListSize(list_size):
            print("Couldn't get device list size")
        if list_size[0] == 0:
            return []
        device_list = DeviceList(list_size=list_size[0])
        if self.pozyx.getDeviceIds(device_list) == POZYX_SUCCESS:
            print("Discovery success! devices found: %s" % str(device_list))
            return device_list.data
        else:
            print("Discovery failed, found %i devices" % list_size[0])
            # tries to discover the devices again until status is success and a device list is returned
            # beware not to get stuck in endless loop.
            return self.discover_devices()

    def change_settings(self, device_ids):
        """Changes the device's UWB settings"""
        for device_id in device_ids:
            if device_id in self.devices and device_id not in self.encountered:
                while not self.pozyx.setUWBSettings(self.uwb_settings, device_id):
                    print("Not able to set UWB settings on device 0x%0.4x" %
                          device_id)
                self.encountered.append(device)
                print("Successfully set UWB settings on device 0x%0.4x" %
                      device_id)

    def save_settings(self):
        """Saves the UWB settings to flash on all devices"""
        # set the UWB settings to the desired one
        self.pozyx.setUWBSettings(self.uwb_settings)
        registers = [POZYX_UWB_CHANNEL, POZYX_UWB_RATES,
                     POZYX_UWB_PLEN, POZYX_UWB_GAIN]
        for device_id in self.devices:
            while not self.pozyx.saveRegisters(registers, device_id):
                print("Not able to save UWB settings on device 0x%0.4x" %
                      device_id)
            print("Successfully saved UWB settings on device 0x%0.4x" % device_id)


if __name__ == "__main__":
    s = SetSameUWBSettings(port, uwb_settings, devices, save_to_flash)
