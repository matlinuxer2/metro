[collect ./source/stage3.spec]
[collect ./target/stage4.spec]

[section stage4]

target/name: liveimg

[section path/mirror]

target/basename: $[target/name].tar.$[target/compression]
target/latest: $[target/name/latest].tar.$[target/compression]
target/full_latest: $[target/name/full_latest].tar.$[target/compression]

[section steps]
common/inc: [
if [ "$CUR_STATE" = "unpack_post" -o "$CUR_STATE" = "capture" ];then
	export FROM_DIR="$[path/live_in_chroot]/"
	export CHROOT_DIR="$[path/chroot]/"
	export MIRROR_DIR="$[path/mirror/source/subpath]/"
	export OUT_DIR="$(dirname $[path/mirror/target])"
	export STAGE_DIR="$[path/chroot/stage]"
	export TARGET_NAME="$[target/name]"
	export TARGET_DONE="$OUT_DIR/$TARGET_NAME"
	export TARGET_ROOTFS="$OUT_DIR/rootfs-$TARGET_NAME.squashfs"
	export TARGET_KERNRL="$OUT_DIR/kernel-$TARGET_NAME"
	export TARGET_KERNRL_CONFIG="$OUT_DIR/kernel-config-$TARGET_NAME"
	export TARGET_KERNCACHE="$OUT_DIR/kerncache-$TARGET_NAME.tar.bz2"
	export TARGET_INITRAMFS="$OUT_DIR/initramfs-$TARGET_NAME.cpio.gz"
fi

function mirror_scripts(){
if [ "$CUR_STATE" = "unpack_post" -o "$CUR_STATE" = "capture" ];then
	if [ -d "$CHROOT_DIR" -a -d "$FROM_DIR" ];then
		echo "Syncing live seeds $FROM_DIR ---> $CHROOT_DIR ..."
		rsync -avz "$FROM_DIR" "$CHROOT_DIR"
	fi
fi
}

function feedback_scripts(){
if [ "$CUR_STATE" = "unpack_post" -o "$CUR_STATE" = "capture" ];then
	if [ -d "$CHROOT_DIR" -a -d "$FROM_DIR" ];then
		echo "Syncing live seeds $FROM_DIR <--- $CHROOT_DIR ..."
		pushd . ; cd "$FROM_DIR"
		for ff in `find . -type f`
		do
			cp --update -v "$CHROOT_DIR/$ff" "$FROM_DIR/$ff"
		done
		popd
	fi
fi
}

function launch_shell(){
	echo "==== Enter shell ( MODE: $CUR_STATE ) ==================="
if [ "$CUR_STATE" = "chroot_run" ];then
	pushd . ; cd /tmp/ ; bash ;popd
else
	pushd . ; cd $CHROOT_DIR/tmp/ ; bash ;popd
fi
	echo "========================================================="
}

function launch_scripts(){
if [ "$CUR_STATE" = "chroot_run" ];then
	INITRUN="/tmp/live/run_hooks"
else
	INITRUN="$CHROOT_DIR/tmp/live/run_hooks"
fi

	if [ -f $INITRUN ]; then
		echo "Start scripts >>>$INITRUN<<<..."
		chmod +x $INITRUN
		$INITRUN "$CUR_STATE"
	fi
}

]

common/run: [

mirror_scripts
launch_scripts
launch_shell
feedback_scripts

]

unpack/post: [
#!/bin/bash

export CUR_STATE="unpack_post"
$[[steps/common/inc:lax]]
$[[steps/common/run:lax]]

]

chroot/run: [
#!/bin/bash
$[[steps/setup]]

export CUR_STATE="chroot_run"
$[[steps/common/inc:lax]]
$[[steps/common/run:lax]]

]

capture: [
#!/bin/bash

export CUR_STATE="capture"
$[[steps/common/inc:lax]]
$[[steps/common/run:lax]]

]
