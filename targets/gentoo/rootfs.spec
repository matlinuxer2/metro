[collect ./source/stage3.spec]
[collect ./target/stage4.spec]
[collect ./stage/capture/squashfs.spec]
[section stage4]

target/name: rootfs

[section path/mirror]

target/basename: $[target/name].squashfs
target/latest: $[target/name/latest].squashfs
target/full_latest: $[target/name/full_latest].squashfs


[section steps]
unpack/post: [
#!/bin/bash

FROM_DIR="$[path/live_in_chroot]/"
CHROOT_DIR="$[path/chroot]/"
MIRROR_SRC_DIR="$[path/mirror]/$[path/mirror/source/subpath]"
KERN_FILENAME="$[target/build]-$[target/subarch]-kernel-$[target/version].tar.bz2"
kerncache="$MIRROR_SRC_DIR/$KERN_FILENAME"

if [ -d "$CHROOT_DIR" -a -d "$FROM_DIR" ]; then
		echo "Syncing live seeds from $FROM_DIR to $CHROOT_DIR ..."
		rsync -avz "$FROM_DIR" "$CHROOT_DIR"
fi



if [ -e "$kerncache" ]; then
        echo "Coping kerncache $kerncache..."
        cp  $kerncache $CHROOT_DIR/tmp/kerncache.tar.bz2
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
	|| ( exit 1 )

### To patch genkernel here
vim -i NONE -e -X -c ':123 move 117' -c':wq' $(which genkernel)

genkernel --no-clean --no-mountboot \
        --no-kernel-sources \
	--kerncache=/tmp/kerncache.tar.bz2 \
	kernel

#export USE="$[portage/USE] bindist"
emerge --update --autounmask=y --autounmask-write $eopts @mat \
	       || emerge --update $eopts @mat \
	       || ( exit 1 )

emerge $eopts --oneshot net-dialup/mingetty

sed -i -e '/^c/s!agetty 38400!mingetty --autologin root --noclear!' /etc/inittab || exit 1

]
