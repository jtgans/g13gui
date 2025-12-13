import gi
import time
import threading

from builtins import property

from g13gui.observer.observer import Observer
from g13gui.observer.subject import ChangeType
from g13gui.applet.applet import BUTTONS
from g13gui.applet.loopbackdisplaydevice import LoopbackDisplayDevice
from g13gui.bitwidgets.display import Display
from g13gui.bitwidgets.screen import Screen
from g13gui.bitwidgets.label import Label
from g13gui.bitwidgets.button import Button
from g13gui.bitwidgets.glyph import Glyphs
from g13gui.bitwidgets.listview import ListView

gi.require_version('GLib', '2.0')
from gi.repository import GLib


class Switcher(Observer):
    def __init__(self, appletManager):
        Observer.__init__(self)

        self._appletManager = appletManager
        self._applets = []

        self._appletManager.registerObserver(self, {'activeApplet', 'applet'})
        self.changeTrigger(self.onAppletChange, keys={'applet'})

        self._initWidgets()

    @property
    def bus_name(self):
        return self

    def onAppletChange(self, subject, changeType, key, data):
        self._applets = {}
        registry = self._appletManager.applets.copy()
        for dbus_name, proxy in registry.items():
            if proxy == self:
                continue
            name = str(proxy.GetName())
            self._applets[name] = str(dbus_name)

        self._lv.model = sorted(self._applets.keys())
        self._lv.update()

        self._s.nextFrame()
        frame = self._dd.frame
        self._appletManager.Present(frame, self)

        print(repr(self._applets))

    def _initWidgets(self):
        self._dd = LoopbackDisplayDevice()
        self._d = Display(self._dd)
        self._s = Screen(self._d)

        self._lv = ListView(self._applets)
        self._lv.showAll()
        self._s.addChild(self._lv)

        button = Button(Glyphs.DOWN_ARROW)
        self._s.buttonBar.setButton(1, button)
        button = Button(Glyphs.UP_ARROW)
        self._s.buttonBar.setButton(2, button)
        button = Button(Glyphs.CHECKMARK)
        self._s.buttonBar.setButton(3, button)
        self._s.buttonBar.showAll()

    def _setButtonPressed(self, state, button):
        if button in BUTTONS:
            buttonIdx = BUTTONS.index(button)
            button = self._s.buttonBar.button(buttonIdx)
            if button:
                button.pressed = state

    def Present(self, timestamp, **kwargs):
        self._s.show()
        self._lv.update()
        self._s.nextFrame()
        frame = self._dd.frame
        return frame

    def Unpresent(self):
        self._s.hide()

    def KeyPressed(self, timestamp, key):
        self._setButtonPressed(True, key)
        return self.Present(timestamp)

    def _setActiveApplet(self):
        selectedName = self._lv.selection()
        if selectedName:
            self._appletManager.activeApplet = self._applets[selectedName]

    def KeyReleased(self, timestamp, key):
        self._setButtonPressed(False, key)

        if key == 'L2':    # down
            self._lv.nextSelection()
        elif key == 'L3':  # up
            self._lv.prevSelection()
        elif key == 'L4':  # select
            GLib.idle_add(self._setActiveApplet)

        return self.Present(timestamp)
