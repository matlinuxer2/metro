[collect ./source/stage3.spec]
[collect ./target/stage4.spec]

[section stage4]

target/name: liveimg

[section path/mirror]

target/basename: $[target/name].tar.$[target/compression]
target/latest: $[target/name/latest].tar.$[target/compression]
target/full_latest: $[target/name/full_latest].tar.$[target/compression]

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

echo "==== Enter shell <unpack/post> ==============="
bash 
echo "=============================================="

]

chroot/run: [
#!/bin/bash
$[[steps/setup]]

INIT="/tmp/live/run_in_chroot"

if [ -f $INIT ]; then
        echo "Start build script >>>$INIT<<<..."
	chmod +x $INIT
	$INIT || (bash ; exit 1 )
fi

echo "==== Enter shell <chroot/run> ================"
bash 
echo "=============================================="

]

capture: [
#!/bin/bash

export OUT_DIR="$(dirname $[path/mirror/target])"
export STAGE_DIR="$[path/chroot/stage]"
export 
export TARGET_NAME="$[target/name]"
export TARGET_DONE="$OUT_DIR/$TARGET_NAME"
export TARGET_ROOTFS="$OUT_DIR/rootfs-$TARGET_NAME.squashfs"
export TARGET_KERNRL="$OUT_DIR/kernel-$TARGET_NAME"
export TARGET_KERNRL_CONFIG="$OUT_DIR/kernel-config-$TARGET_NAME"
export TARGET_KERNCACHE="$OUT_DIR/kerncache-$TARGET_NAME.tar.bz2"
export TARGET_INITRAMFS="$OUT_DIR/initramfs-$TARGET_NAME.cpio.gz"


if [ ! -d $OUT_DIR ]
then
	install -d $OUT_DIR || exit 1
fi

if [ -f $STAGE_DIR/boot/kerncache.tar.bz2 ]; then
	cp $STAGE_DIR/boot/kerncache.tar.bz2 $TARGET_KERNCACHE 
fi

kernel_pathname="$(find $STAGE_DIR/boot/ -name 'kernel*' -type f | head -n 1)"
cp $kernel_pathname $TARGET_KERNRL
cp $[path/chroot/stage]/usr/src/linux/.config $TARGET_KERNRL_CONFIG

#mksquashfs $STAGE_DIR $TARGET_ROOTFS
#if [ $? -ge 2 ]; then
#	rm -f "$TARGET_ROOTFS" 
#	exit 1
#elif [ $? -ne 0 ]; then
#	echo "Compression error - aborting."
#	rm -f $[path/mirror/target]
#	exit 99
#fi

echo "==== Enter shell <capture> ==================="
bash 
echo "=============================================="

]
