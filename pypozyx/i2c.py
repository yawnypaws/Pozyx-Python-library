# I2C POZYX IMPLEMENTATION
# Not implemented yet

from pypozyx.lib import PozyxLib
from pypozyx.definitions.constants import *
from pypozyx.definitions.registers import *


class PozyxI2C(PozyxLib):

    def __init__(self, mode=MODE_POLLING, print_output=False):
        pass

    def regWrite(self, address, data):
        pass

    def regRead(self, address, data):
        pass

    def regFunction(self, address, params, data):
        pass

    #
    def waitForFlag(self, interrupt_flag, timeout_ms, interrupt):
        pass

    #
    def waitForFlag_safe(self, interrupt_flag, timeout_ms, interrupt):
        pass
