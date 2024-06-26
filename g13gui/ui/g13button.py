import gi

import g13gui.ui as ui
from g13gui.observer.gtkobserver import GtkObserver
from g13gui.model.bindings import BindsToKeynames

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, GObject, Gdk


class G13Button(Gtk.MenuButton, GtkObserver):
    def __init__(self, prefs, g13KeyName):
        Gtk.MenuButton.__init__(self)
        GtkObserver.__init__(self)

        self._prefs = prefs
        self._keyName = g13KeyName
        self._lastProfileName = None

        self._prefs.registerObserver(self, {'selectedProfile', self._keyName})
        self.changeTrigger(self.onSelectedProfileChanged,
                           keys={'selectedProfile'})
        self.changeTrigger(self.onBindingChanged, keys={self._keyName})

        self._popover = ui.G13ButtonPopover(self, self._prefs, self._keyName)
        self.set_popover(self._popover)

        self.set_size_request(100, 25)
        self.set_can_default(False)
        self.updateProfileRegistration()

        self.connect('show', self.onShown)

    def onShown(self, widget):
        self.updateBindingDisplay()

    def onSelectedProfileChanged(self, subject, changeType, key, data):
        self.updateProfileRegistration()
        self.updateBindingDisplay()

    def onBindingChanged(self, subject, changeType, key, data):
        self.updateBindingDisplay()

    def updateProfileRegistration(self):
        if self._lastProfileName:
            if self._lastProfileName in self._prefs.profileNames():
                lastProfile = self._prefs.profiles(self._lastProfileName)
                lastProfile.removeObserver(self)

        self._prefs.selectedProfile().registerObserver(self, {self._keyName})

    def _removeChild(self):
        child = self.get_child()
        if child:
            self.remove(child)

    def updateBindingDisplay(self):
        self._removeChild()
        bindings = self._prefs.selectedProfile().keyBinding(self._keyName)
        label = Gtk.Label('')
        label.set_halign(Gtk.Align.CENTER)
        label.set_ellipsize(2)
        label.set_max_width_chars(10)
        label.set_width_chars(10)

        if len(bindings) > 0:
            keybinds = BindsToKeynames(bindings)
            accelerator = '+'.join(keybinds)
            label.set_text(accelerator)
        else:
            label.set_text(self._keyName)
            label.set_sensitive(False)

        self.add(label)
        self.show_all()
