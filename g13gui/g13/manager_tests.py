#!/usr/bin/python

import unittest
import time
import usb.util

from g13gui.observer.observer import ObserverTestCase
from g13gui.model.prefs import Preferences
from g13gui.g13.manager import DeviceManager
from g13gui.g13.manager import LCD_BUFFER_SIZE


class DeviceManagerTests(ObserverTestCase):
    def setUp(self):
        prefs = Preferences()
        self.m = DeviceManager(prefs)
        self.m.start()

        while self.m.state != DeviceManager.State.FOUND:
            time.sleep(1)

        self.assertEqual(self.m.state, DeviceManager.State.FOUND)

    def tearDown(self):
        self.m.shutdown()
        self.m.join()

    def testLeds(self):
        for i in range(0, 17):
            self.m.setLedsMode(i)

    def testBacklight(self):
        for i in range(0, 256):
            self.m.setBacklightColor(i, 0, 0)

        for i in range(0, 256):
            self.m.setBacklightColor(0, i, 0)

        for i in range(0, 256):
            self.m.setBacklightColor(0, 0, i)

        for i in range(0, 256):
            self.m.setBacklightColor(i, i, 0)

        for i in range(0, 256):
            self.m.setBacklightColor(0, i, i)

        for i in range(0, 256):
            self.m.setBacklightColor(i, 0, i)

        for i in range(0, 256):
            self.m.setBacklightColor(i, i, i)

    def testLCD(self):
        whiteBuffer = [0x5A] * LCD_BUFFER_SIZE
        blackBuffer = [0xA5] * LCD_BUFFER_SIZE

        for i in range(1, 10):
            self.m.setLCDBuffer(whiteBuffer)
            time.sleep(0.5)
            self.m.setLCDBuffer(blackBuffer)
            time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()
