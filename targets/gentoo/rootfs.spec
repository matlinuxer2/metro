[collect ./source/stage3.spec]
[collect ./target/stage4.spec]
[collect ./stage/capture/squashfs.spec]

[section path/mirror]

target: $[:source/subpath]/$[target/name].squashfs

[section target]

name: rootfs-$[:subarch]-$[:build]-$[:version]

[section steps]
unpack/post: [
#!/bin/bash

FROM_DIR="$[path/live_in_chroot]/"
CHROOT_DIR="$[path/chroot]/"
MIRROR_DIR="$[path/mirror/source/subpath]/"

if [ -d "$CHROOT_DIR" ];then

	if [ -d "$FROM_DIR" ]; then
		echo "Syncing live seeds from $FROM_DIR to $CHROOT_DIR ..."
		rsync -avz "$FROM_DIR" "$CHROOT_DIR"
	fi

	if [ -d "$MIRROR_DIR" ]; then
		echo "Retrieve done list..."
		ls > $CHROOT_DIR/tmp/done.list
	fi
fi

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

#export USE="$[portage/USE] bindist"
emerge --update --autounmask=y --autounmask-write $eopts @mat \
	       || emerge --update $eopts @mat \
	       || ( bash ; exit 1 )

emerge $eopts --oneshot net-dialup/mingetty

sed -i -e '/^c/s!agetty 38400!mingetty --autologin root --noclear!' /etc/inittab || exit 1

]

[section portage]

ROOT: /
