Name:          g13gui
Version:       0.1.0
Release:       1
Summary:       A user-space driver and GUI configurator for the Logitech G13
License:       BSD
URL:           https://github.com/jtgans/g13gui
Requires:      python3-dbus
Requires:      python3-appdirs
Requires:      python3-evdev
Requires:      python3-pillow
Requires:      python3-gobject
Requires:      python3-pyusb
Requires:      gtk3
Requires:      libappindicator-gtk3
Source:        g13gui-%{version}.tar.gz
BuildRequires: meson

%description
This is the companion application to the Logitech G13 gameboard, and provides
both configuration tooling, applet hosting, and also a user space driver to
handle translation of keypresses to real Linux input events by way of uinput.

# Need this definition, or else meson_install trips up trying to find debug info
%define debug_package %{nil}

%prep
%autosetup -c

%build
%meson
%meson_build

%install
%meson_install

%check
%meson_test

%files
/usr/bin/g13-clock
/usr/bin/g13-profiles
/usr/bin/g13gui
/usr/lib/python3.*/site-packages/g13gui/*
/usr/lib/udev/rules.d/91-g13.rules
/usr/share/applications/com.theonelab.g13.*.desktop
/usr/share/icons/hicolor/*

