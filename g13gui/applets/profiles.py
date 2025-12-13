import gi
import time
import enum

from g13gui.applet.applet import Applet
from g13gui.applet.applet import BUTTONS
from g13gui.applet.applet import RunApplet
from g13gui.bitwidgets.listview import ListView
from g13gui.bitwidgets.button import Button
from g13gui.bitwidgets.glyph import Glyphs

gi.require_version('GLib', '2.0')
from gi.repository import GLib


class ProfilesApplet(Applet):
    NAME = 'Profiles'
    BUS_NAME = Applet.MakeBusName('profiles')

    def __init__(self):
        Applet.__init__(self, ProfilesApplet.BUS_NAME, ProfilesApplet.NAME)

        self._profiles = []
        self._selectedProfile = None

        self._lv = ListView(self._profiles)
        self._lv.showAll()
        self.screen.addChild(self._lv)

        button = Button(Glyphs.DOWN_ARROW)
        self.screen.buttonBar.setButton(1, button)
        button = Button(Glyphs.UP_ARROW)
        self.screen.buttonBar.setButton(2, button)
        button = Button(Glyphs.CHECKMARK)
        self.screen.buttonBar.setButton(3, button)
        self.screen.buttonBar.showAll()

    def _updateProfileStates(self):
        profiles = [str(x) for x in self.manager.GetProfiles()]
        self._profiles.clear()
        self._profiles.extend(profiles)
        self._selectedProfile = str(self.manager.GetSelectedProfile())

    def _updateListView(self):
        if self._selectedProfile:
            self._lv.markedIndex = self._profiles.index(self._selectedProfile)
        self._lv.model = self._profiles
        self._lv.update()

    def _updateAndPresent(self):
        self._updateProfileStates()
        self._updateListView()
        self.maybePresentScreen()

    def onRegistered(self):
        self._updateProfileStates()

    def onShown(self, timestamp):
        self._updateListView()
        GLib.idle_add(self._updateAndPresent)

    def _setActiveProfile(self):
        selectedProfile = self._lv.selection()
        self.manager.SetSelectedProfile(selectedProfile)
        self._updateAndPresent()

    def onKeyReleased(self, timestamp, key):
        if key == 'L2':    # down
            self._lv.nextSelection()
        elif key == 'L3':  # up
            self._lv.prevSelection()
        elif key == 'L4':  # select
            self._lv.markSelection()
            GLib.idle_add(self._setActiveProfile)


def main():
    RunApplet(ProfilesApplet)


if __name__ == '__main__':
    main()
