import gi
import dbus
import dbus.service
import dbus.mainloop.glib
import time

from dbus.mainloop.glib import DBusGMainLoop
from dbus.exceptions import DBusException
from dbus.types import ByteArray

from g13gui.applet.loopbackdisplaydevice import LoopbackDisplayDevice
from g13gui.bitwidgets.display import Display
from g13gui.bitwidgets.screen import Screen

gi.require_version('GLib', '2.0')
from gi.repository import GLib


BUTTONS = [
    'L1', 'L2', 'L3', 'L4'
]


class Applet(dbus.service.Object):
    BUS_INTERFACE_NAME = 'com.theonelab.g13.Applet'
    BUS_PATH = '/com/theonelab/g13/applets'
    BUS_NAME_PREFIX = 'com.theonelab.g13.applets.'

    def MakeBusName(name):
        return Applet.BUS_NAME_PREFIX + name

    def __init__(self, bus_name, name):
        self._bus = dbus.SessionBus()
        self._busName = dbus.service.BusName(bus_name,
                                             bus=self._bus,
                                             replace_existing=False,
                                             do_not_queue=True)
        dbus.service.Object.__init__(self,
                                     self._bus,
                                     Applet.BUS_PATH)
        print(f'Applet {name} registered with dbus as {bus_name}')

        self._name = name
        self._dd = LoopbackDisplayDevice()
        self._d = Display(self._dd)
        self._s = Screen(self._d)
        self._s.hide()

    def _discoverManager(self):
        try:
            self._manager = self._bus.get_object('com.theonelab.g13.AppletManager',
                                                 '/com/theonelab/g13/AppletManager')
            GLib.timeout_add_seconds(5, self._discoverManager)
        except DBusException:
            GLib.timeout_add_seconds(1, self._discoverManager)

    def _setButtonPressed(self, state, button):
        if button in BUTTONS:
            buttonIdx = BUTTONS.index(button)
            button = self._s.buttonBar.button(buttonIdx)
            if button:
                button.pressed = state

    def run(self):
        self._bus = dbus.SessionBus()
        self._discoverManager()
        loop = GLib.MainLoop()
        loop.run()

    @property
    def name(self):
        return self._name

    @property
    def displayDevice(self):
        return self._dd

    @property
    def display(self):
        return self._d

    @property
    def screen(self):
        return self._s

    @property
    def manager(self):
        return self._manager

    def onKeyPressed(self, timestamp, key):
        pass

    def onKeyReleased(self, timestamp, key):
        pass

    def onShown(self, timestamp):
        pass

    def onHidden(self):
        pass

    def onRegistered(self):
        pass

    def onUnregistered(self):
        pass

    def maybePresentScreen(self):
        if self.screen.visible and self._manager:
            self.screen.nextFrame()
            frame = self.displayDevice.frame
            frame = ByteArray(frame)
            self._manager.Present(frame, byte_arrays=True)

    @dbus.service.method(BUS_INTERFACE_NAME,
                         out_signature='s')
    def GetName(self):
        return self._name

    @dbus.service.method(BUS_INTERFACE_NAME,
                         in_signature='d', out_signature='ay',
                         byte_arrays=True)
    def Present(self, timestamp):
        self.screen.show()
        self.onShown(timestamp)
        self.screen.nextFrame()
        return ByteArray(self.displayDevice.frame)

    @dbus.service.method(BUS_INTERFACE_NAME)
    def Unpresent(self):
        self.screen.hide()
        self.onHidden()

    @dbus.service.method(BUS_INTERFACE_NAME,
                         in_signature='di', out_signature='ay',
                         byte_arrays=True)
    def KeyPressed(self, timestamp, key):
        self.onKeyPressed(timestamp, key)
        self._setButtonPressed(True, key)
        self.screen.nextFrame()
        return ByteArray(self.displayDevice.frame)

    @dbus.service.method(BUS_INTERFACE_NAME,
                         in_signature='di', out_signature='ay',
                         byte_arrays=True)
    def KeyReleased(self, timestamp, key):
        self.onKeyReleased(timestamp, key)
        self._setButtonPressed(False, key)
        self.screen.nextFrame()
        return ByteArray(self.displayDevice.frame)


def RunApplet(cls, *args, **kwargs):
    DBusGMainLoop(set_as_default=True)
    applet = cls(*args, **kwargs)
    applet.run()
