import gi
import dbus
import dbus.service
import dbus.mainloop.glib
import time
import threading

from builtins import property

from g13gui.observer.subject import Subject
from g13gui.observer.subject import ChangeType
from g13gui.applets.switcher import Switcher
from g13gui.applet.applet import Applet
from g13gui.g13.common import G13Keys

gi.require_version('GLib', '2.0')
from gi.repository import GLib


class AppletManager(dbus.service.Object, Subject):
    INTERFACE_NAME = 'com.theonelab.g13.AppletManager'
    BUS_NAME = 'com.theonelab.g13.AppletManager'
    BUS_PATH = '/com/theonelab/g13/AppletManager'

    def __init__(self, deviceManager, prefs):
        self._bus = dbus.SessionBus()
        self._busName = dbus.service.BusName(AppletManager.BUS_NAME, self._bus)
        dbus.service.Object.__init__(self, self._bus,
                                     AppletManager.BUS_PATH)
        Subject.__init__(self)

        self._deviceManager = deviceManager
        self._prefs = prefs
        self._datastore = {}

        self._switcher = Switcher(self)
        self._lastApplet = self._switcher
        self._activeApplet = self._switcher

        # map of dbus name -> proxy
        self._applets = {}
        self._applets['Switcher'] = self._switcher

        self._threads = []

        self.addChange(ChangeType.ADD, 'applet', 'Switcher')
        self.notifyChanged()

    def _startAppletThread(self, bus, name):
        while True:
            print(f'Attempting to start applet {name}')
            try:
                bus.activate_name_owner(name)
                proxy = bus.get_object(name, Applet.BUS_PATH)
                self._applets[name] = proxy
                print(f'Found {name}')
                self.addChange(ChangeType.ADD, 'applet', name)
                self.notifyChanged()
                return
            except dbus.DBusException as err:
                print(f'Failed to activate applet: {err}')
            time.sleep(1)

    def discoverAndStartApplets(self):
        bus = dbus.SessionBus()
        bus.add_signal_receiver(self._onInterfaceAdded,
                                signal_name='InterfacesAdded',
                                dbus_interface=Applet.BUS_INTERFACE_NAME,
                                path='/org/freedesktop/DBus',
                                sender_keyword='sender')
        bus.add_signal_receiver(self._onInterfaceRemoved,
                                signal_name='InterfacesRemoved',
                                dbus_interface=Applet.BUS_INTERFACE_NAME,
                                path='/org/freedesktop/DBus',
                                sender_keyword='sender')

        print('Starting initial activatable services...')
        for name in bus.list_activatable_names():
            print(f'Investigating {name}')
            if name.startswith(Applet.BUS_NAME_PREFIX):
                print(f'Starting {name}...')
                thread = threading.Thread(target=self._startAppletThread, args=(bus, str(name)))
                self._threads.append(thread)
                thread.start()
        print('Initial discovery complete.')

    def _onInterfaceAdded(self, sender):
        print(f'onInterfaceAdded: {sender}')
        pass

    def _onInterfaceRemoved(self, sender):
        print(f'onInterfaceRemoved: {sender}')
        pass

    def stopApplets(self):
        pass

    @property
    def activeApplet(self):
        return self._activeApplet

    @activeApplet.setter
    def activeApplet(self, appletName):
        appletProxy = self._applets[appletName]

        try:
            self._activeApplet.Unpresent()
            self._lastApplet = self._activeApplet
        except dbus.exceptions.DBusException as err:
            print('Failed to unpresent active applet: %s' % (err))
            self._removeActiveApplet()

        self.setProperty('activeApplet', appletProxy)
        self.onPresent()

    def swapApplets(self):
        try:
            self._activeApplet.Unpresent()
        except dbus.exceptions.DBusException as err:
            print('Failed to unpresent active applet: %s' % (err))
            self._removeActiveApplet()
            self._lastApplet = self._switcher
            self.setProperty('activeApplet', self._switcher)
        else:
            lastApplet = self._lastApplet
            self._lastApplet = self._activeApplet
            self.setProperty('activeApplet', lastApplet)
        finally:
            self.onPresent()

    def raiseSwitcher(self):
        self._activeApplet = self._switcher
        self.onPresent()

    @property
    def applets(self):
        return self._applets

    def _updateLCD(self, frame):
        self._deviceManager.setLCDBuffer(frame)

    def _removeActiveApplet(self):
        try:
            # name = self._applets[self._activeApplet]
            # del self._applets[name]
            # self.addChange(ChangeType.REMOVE, 'applet', name)
            pass
        except KeyError as err:
            print('Desync occurred: senders does not contain %s!',
                  (self._activeApplet))

        self._activeApplet = self._switcher
        self._lastApplet = self._switcher
        self.activeApplet = 'Switcher'

    def onPresent(self):
        try:
            frame = self._activeApplet.Present(time.time(), byte_arrays=True)
            frame = bytes(frame)
            self._updateLCD(frame)
        except dbus.exceptions.DBusException as err:
            print('Failed to present applet: %s' % (err))
            self._removeActiveApplet()

    def onKeyPressed(self, keyname):
        # Swap to the switcher
        if keyname == 'BD':
            self.swapApplets()
            return

        try:
            frame = self._activeApplet.KeyPressed(time.time(),
                                                  keyname)
            self._updateLCD(frame)
        except dbus.exceptions.DBusException as err:
            print('Failed to send keyPressed for applet: %s' % (err))
            self._removeActiveApplet()

    def onKeyReleased(self, keyname):
        try:
            frame = self._activeApplet.KeyReleased(time.time(),
                                                   keyname)
            self._updateLCD(frame)
        except dbus.exceptions.DBusException as err:
            print('Failed to send keyReleased for applet: %s' % (err))
            self._removeActiveApplet()

    def _presentScreen(self, screen, sender):
        self._updateLCD(screen)

    @dbus.service.method(dbus_interface=INTERFACE_NAME,
                         in_signature='ay', sender_keyword='sender',
                         byte_arrays=True)
    def Present(self, screen, sender):
        if self._activeApplet.bus_name != sender:
            print('Sender %s is not the active applet.' % (sender))
            return
        GLib.idle_add(self._presentScreen, screen, sender)

    @dbus.service.method(dbus_interface=INTERFACE_NAME,
                         out_signature='as',
                         sender_keyword='sender')
    def GetProfiles(self, sender):
        return self._prefs.profileNames()

    @dbus.service.method(dbus_interface=INTERFACE_NAME,
                         out_signature='s',
                         sender_keyword='sender')
    def GetSelectedProfile(self, sender):
        return self._prefs.selectedProfileName()

    @dbus.service.method(dbus_interface=INTERFACE_NAME,
                         in_signature='s', out_signature='b',
                         sender_keyword='sender')
    def SetSelectedProfile(self, profileName, sender):
        if profileName not in self._prefs.profileNames():
            print('Sender %s attempted to set nonexistant profile %s' %
                  (sender, profileName))
            return False

        GLib.idle_add(self._prefs.setSelectedProfile, profileName)

    @dbus.service.method(dbus_interface=INTERFACE_NAME,
                         in_signature='ss',
                         sender_keyword='sender')
    def SetKey(self, keyName, data, sender):
        self._datastore[keyName] = data

    @dbus.service.method(dbus_interface=INTERFACE_NAME,
                         in_signature='s', out_signature='s',
                         sender_keyword='sender')
    def GetKey(self, keyName, sender):
       return self._datastore.get(keyName, '')

