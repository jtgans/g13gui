project(
  'g13gui',
  license: 'MIT'
)

python = import('python').find_installation()

prefix = get_option('prefix')
bindir = get_option('bindir')
datadir = get_option('datadir')
etcdir = get_option('sysconfdir')
prefix = get_option('prefix')
pylibdir = python.get_install_dir()
g13dir = join_paths(pylibdir, 'g13gui')

install_data(
  files('bin/g13gui', 'bin/g13-clock', 'bin/g13-profiles'),
  install_dir: bindir,
  install_mode: 'rwxr-xr-x',
)

install_subdir(
  'g13gui',
  install_dir: pylibdir,
)

install_subdir(
  'etc/icons/hicolor',
  install_dir: join_paths(datadir, 'icons'),
  install_mode: 'rw-r--r--',
)

install_data(
  files('etc/com.theonelab.g13.Configurator.desktop'),
  install_dir: join_paths(datadir, 'applications'),
  install_mode: 'rw-r--r--',
)

install_data(
  files('etc/com.theonelab.g13.applet.clock.service',
        'etc/com.theonelab.g13.applet.profiles.service'),
  install_dir: join_paths(prefix, 'share/dbus-1/services'),
  install_mode: 'rw-r--r--',
)

install_data(
  files('etc/91-g13.rules'),
  install_dir: join_paths(prefix, 'lib/udev/rules.d'),
  install_mode: 'rw-r--r--',
)
