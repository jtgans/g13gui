import gi
import time
import enum
import psutil
import json

from g13gui.applet.applet import Applet
from g13gui.applet.applet import BUTTONS
from g13gui.applet.applet import RunApplet
from g13gui.bitwidgets.label import Label
from g13gui.bitwidgets.fonts import Fonts
from g13gui.bitwidgets.button import LabelButton
from g13gui.bitwidgets.graph import Graph
from g13gui.bitwidgets import DISPLAY_WIDTH

gi.require_version('GLib', '2.0')
from gi.repository import GLib


class ClockMode(enum.Enum):
    HOUR_12 = 1
    HOUR_24 = 2


class ClockApplet(Applet):
    NAME = 'Clock'
    BUS_NAME = Applet.MakeBusName('clock')
    DATASTORE_KEY = 'com.theonelab.g13gui.applets.clock'

    def __init__(self):
        Applet.__init__(self, ClockApplet.BUS_NAME, ClockApplet.NAME)

        self._timeLabel = Label(43, 8, '18:54:00', font=Fonts.LARGE)
        self._timeLabel.showAll()
        self.screen.addChild(self._timeLabel)

        self._modeButtons = {
            ClockMode.HOUR_12: LabelButton('12 hour'),
            ClockMode.HOUR_24: LabelButton('24 hour')
        }
        self._clockMode = ClockMode.HOUR_24
        self._onModeSwitch()

        self._loadGraphToggle = LabelButton('Load', isToggleable=True)
        self._ramGraphToggle = LabelButton('RAM', isToggleable=True)
        self.screen.buttonBar.addChild(self._loadGraphToggle)
        self.screen.buttonBar.addChild(self._ramGraphToggle)
        self.screen.buttonBar.showAll()

        self._loadGraph = Graph(1, 18,
                                DISPLAY_WIDTH // 2 - 5, 12)
        self.screen.addChild(self._loadGraph)

        self._ramGraph = Graph(DISPLAY_WIDTH // 2 + 2, 18,
                               DISPLAY_WIDTH // 2 - 5, 12)
        self.screen.addChild(self._ramGraph)

        self._update()

    def _update(self):
        (tm_year, tm_month, tm_mday, tm_hour,
         tm_min, tm_sec, tm_wday, tm_yday, tm_isdst) = time.localtime()
        ampm = ''

        if self._clockMode == ClockMode.HOUR_12:
            ampm = ' AM'
            if tm_hour >= 12:
                ampm = ' PM'
                if tm_hour > 12:
                    tm_hour -= 12

        self._timeLabel.text = '%d:%0.2d:%0.2d%s' % (
            tm_hour, tm_min, tm_sec, ampm)

        (w, h) = self._timeLabel.bounds
        x = (DISPLAY_WIDTH // 2) - (w // 2)
        self._timeLabel.position = (x, 0)

        self._loadGraph.addValue(psutil.cpu_percent() / 100)
        self._ramGraph.addValue(psutil.virtual_memory().percent / 100)

    def _pushTime(self):
        self._update()
        self.maybePresentScreen()
        return self.screen.visible

    def onShown(self, timestamp):
        self._update()
        GLib.timeout_add_seconds(1, self._pushTime)

    def onUpdateScreen(self):
        self._update()

    def _onModeSwitch(self):
        if self._clockMode == ClockMode.HOUR_12:
            self._clockMode = ClockMode.HOUR_24
            button = self._modeButtons[ClockMode.HOUR_12]
        elif self._clockMode == ClockMode.HOUR_24:
            self._clockMode = ClockMode.HOUR_12
            button = self._modeButtons[ClockMode.HOUR_24]

        button.show()
        self.screen.buttonBar.setButton(0, button)

    def onKeyReleased(self, timestamp, key):
        if key == 'L1':
            self._onModeSwitch()
        elif key == 'L2':
            self._loadGraphToggle.toggle()
            self._loadGraph.visible = self._loadGraphToggle.isOn
        elif key == 'L3':
            self._ramGraphToggle.toggle()
            self._ramGraph.visible = self._ramGraphToggle.isOn
        GLib.idle_add(self._storeSettings)

    def onRegistered(self):
        GLib.idle_add(self._loadSettings)

    def _storeSettings(self):
        settings = json.dumps([
            self._clockMode.value,
            self._loadGraph.visible,
            self._ramGraph.visible
        ])
        print(f'Storing settings [{settings}]')
        self.manager.SetKey(ClockApplet.DATASTORE_KEY, settings)

    def _loadSettings(self):
        settings = self.manager.GetKey(ClockApplet.DATASTORE_KEY)
        print(f'Loaded settings are [{settings}]')
        if settings:
            (clockMode,
             loadGraphVisible,
             ramGraphVisible) = json.loads(settings)
            self._clockMode = ClockMode(clockMode)
            self._loadGraph.visible = loadGraphVisible
            self._loadGraphToggle.isOn = loadGraphVisible
            self._ramGraph.visible = ramGraphVisible
            self._ramGraphToggle.isOn = ramGraphVisible
            self._onModeSwitch()
            self._update()


def main():
    RunApplet(ClockApplet)


if __name__ == '__main__':
    main()
