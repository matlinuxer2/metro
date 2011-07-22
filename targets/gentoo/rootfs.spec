[collect ./stage/common.spec]
[collect ./stage/capture/squashfs.spec]
[collect ./stage/stage3-derivative.spec]

[section path/mirror]

target: $[:source/subpath]/$[target/name].squashfs

[section target]

name: rootfs-$[:subarch]-$[:build]-$[:version]

[section steps]
unpack/post: [
#!/bin/bash

kerncache="$[path/mirror/source/subpath]/kernel-$[target/subarch]-$[target/build]-$[target/version].tar.bz2"

if [ -e "$kerncache" ]; then
        echo "Coping kerncache $kerncache..."
        cp  $kerncache $[path/chroot]/tmp/kerncache.tar.bz2
else
        echo "Required file $kerncache not found. ..."
	exit 1
fi

]

chroot/run: [
#!/bin/bash
$[[steps/setup]]

#eselect profile set 1

emerge $eopts --getbinpkg=y --usepkg=y \
        sys-kernel/genkernel \
	|| (bash ; exit 1 )

### To patch genkernel here
vim -i NONE -e -X -c ':123 move 117' -c':wq' $(which genkernel)

genkernel --no-clean --no-mountboot \
        --no-kernel-sources \
	--kerncache=/tmp/kerncache.tar.bz2 \
	kernel

if [ -d "/usr/portage/_etc/" ]; then
        echo "Coping portage settings ..."
	rsync -avz /usr/portage/_etc/ /etc/
fi

export USE="$[portage/USE] bindist"
emerge --update $eopts @mat || ( bash ; exit 1 )

emerge $eopts --oneshot net-dialup/mingetty

sed -i -e '/^c/s!agetty 38400!mingetty --autologin root --noclear!' /etc/inittab || exit 1

]

[section portage]

ROOT: /
