# Maintainer: June Tate-Gans <june@theonelab.com>

pkgbase="g13gui"
pkgname="g13gui-git"
pkgrel=1
pkgver="(replaceme)"
pkgdesc="A user-space driver and GUI configurator for the Logitech G13"
arch=('any')
url="https://github.com/jtgans/g13gui"
license=('MIT')
depends=(
  'python>=3.8'
  'python-appdirs'
  'python-cffi'
  'python-dbus'
  'python-evdev'
  'python-gobject'
  'python-pillow>=10.0.1'
  'python-psutil'
  'python-pyusb>=1.0.2'
  'python-xlib'
  'gtk3'
  'xorg-fonts-misc'
)
makedepends=('git' 'meson')
source=("${pkgname}::git+http://github.com/jtgans/g13gui.git")
sha256sums=('SKIP')

pkgver() {
    cd "${srcdir}"
    git rev-parse --short HEAD
}

prepare() {
    cd "${srcdir}"
    git checkout master
}

build() {
    arch-meson "${srcdir}/${pkgname}" build
}

package() {
    meson install -C build --destdir "${pkgdir}"
}
