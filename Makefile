VERSION   := `grep "VERSION" g13gui/common.py |awk '{ print $$3 }' |tr -d "'"`
GITBRANCH ?= master
PIPENV    := pipenv
PYTHON    := `which python3`
PIP       := ${PYTHON} -m pip

DISTRO    := $(shell \
    lsb_release -i \
        |awk -F: '{ print $$2 }' \
        |sed -e 's/[ \t]*//g' \
        |tr '[A-Z]' '[a-z]' \
        |sed -e 's/linux//g')

ifeq (${DISTRO},ubuntu)
DISTRO := debian
endif

ifeq (${DISTRO},manjaro)
DISTRO := archlinux
else ifeq (${DISTRO},arch)
DISTRO := archlinux
endif

$(warning Building on ${DISTRO})

all: ${DISTRO}

clean: ${DISTRO}-clean
	rm -rf build/
	rm -rf env/

install: ${DISTRO}-install

archlinux:
	mkdir -p build
	makepkg --nodeps
	mv g13gui*.pkg.tar.zst build

archlinux-clean:
	rm -f g13gui-git-*-any.pkg.tar.zst
	rm -rf g13gui-git/
	rm -rf pkg/
	rm -rf src/

archlinux-install:
	makepkg -i

fedora:
	rpmdev-setuptree
	cp g13gui.spec ~/rpmbuild/SPECS
	tar -zcf ~/rpmbuild/SOURCES/g13gui-${VERSION}.tar.gz .
	rpmbuild -bb ~/rpmbuild/SPECS/g13gui.spec
	mkdir -p build
	mv ~/rpmbuild/RPMS/*/g13gui*.rpm build/

fedora-clean:
	rm -rf ~/rpmbuild

fedora-install:
	yum install build/g13gui*.rpm

debian:
	mkdir -p build
	gbp buildpackage --git-verbose --git-ignore-branch --git-debian-branch=$(GITBRANCH) -us -ui -uc
	mv ../g13gui_$(VERSION)* build

debian-install:
	sudo dpkg -i g13gui_$(VERSION).deb

debian-clean:
	debclean

debian-build-source: debian-clean
	mkdir -p build
	gbp buildpackage -S --git-verbose --git-ignore-branch --git-debian-branch=$(GITBRANCH) -us -uc
	mv ../g13gui_$(VERSION)* build

debian-release: debian-build-source

env:
	python3 -m venv env
	tools/in-env python3 -m pip install -r requirements.txt

test: env
	PYTHONPATH=. tools/in-env python3 -m g13gui.tests

dist: clean
	mkdir -p build
	tar --exclude=build --exclude=.drone.yml --exclude-vcs -zcf build/g13gui_$(VERSION).tar.gz .
	docker run -ti -v ${PWD}:/srcs -w /srcs fedora:latest tools/dockerbuild.sh fedora
	docker run -ti -v ${PWD}:/srcs -w /srcs debian:latest tools/dockerbuild.sh debian
	docker run -ti -v ${PWD}:/srcs -w /srcs archlinux:latest tools/dockerbuild.sh archlinux

.PHONY: all clean install test
.PHONY: archlinux archlinux-clean archlinux-install
.PHONY: debian debian-build debian-clean debian-build-source debian-release

