import signal

from g13gui.model.prefsstore import PreferencesStore
from g13gui.g13.manager import DeviceManager
from g13gui.ui.appindicator import AppIndicator
from g13gui.ui.mainwindow import MainWindow

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GLib', '2.0')

from gi.repository import Gtk, GLib, Gio


class Application(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(
            self,
            application_id='com.theonelab.g13.Configurator')

        GLib.set_application_name('G13 Configurator')

        self._prefs = None
        self._indicator = None
        self._dm = None
        self._mainwindow = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        action = Gio.SimpleAction.new('quit')
        action.connect('activate', lambda *x: self.quit())
        self.add_action(action)
        self.add_accelerator('<Primary>q', 'app.quit')

    def do_activate(self):
        if not self._prefs:
            self._prefs = PreferencesStore.getPrefs()
        if not self._indicator:
            self._indicator = AppIndicator(self, self._prefs)
        if not self._dm:
            self._dm = DeviceManager(self._prefs)
            self._dm.start()
        if not self._mainwindow:
            self._mainwindow = MainWindow(self, self._prefs)
        if self._prefs.showWindowOnStart:
            self.showMainWindow()

    def showMainWindow(self):
        self._mainwindow.present()

    def do_shutdown(self):
        if self._mainwindow:
            self._mainwindow.destroy()
        if self._dm:
            self._dm.shutdown()
        Gtk.Application.do_shutdown(self)
