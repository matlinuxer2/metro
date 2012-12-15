[collect ./source/stage3.spec]
[collect ./target/stage4.spec]

[section path/mirror]

target: $[:source/subpath]/$[target/name].cpio.gz

[section target]

name: initramfs-$[:subarch]-$[:build]-$[:version]

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

cat > /etc/portage/package.keywords <<EOF
sys-kernel/dracut ~*
sys-apps/sysvinit ~*
EOF

cat > /etc/portage/package.use<<EOF
dev-libs/libgcrypt static-libs
EOF

emerge $eopts --getbinpkg=y --usepkg=y \
        sys-kernel/genkernel \
	|| (bash ; exit 1 )

### To patch genkernel here
vim -i NONE -e -X -c ':123 move 117' -c':wq' $(which genkernel)


DRACUT_MODULES="dmsquash-live" \
emerge $eopts --getbinpkg=y --usepkg=y --onlydeps --autounmask=y --autounmask-write \
	sys-kernel/dracut

genkernel --no-clean --no-mountboot \
        --no-kernel-sources \
	--kerncache=/tmp/kerncache.tar.bz2 \
	kernel

kernel_pathname="$(find /boot/ -name 'kernel*' -type f | head -n 1)"
initramfs_pathname="${kernel_pathname/kernel-/initramfs-}"
kernel_filename="$( basename ${kernel_pathname} )"
kernel_version="${kernel_filename#kernel-genkernel-*-}"

touch /etc/ld.so.conf.d/empty

export PATH="/tmp/live/dracut/:$PATH"

dracut --verbose \
       --force \
       --modules="base kernel-modules dmsquash-live" \
       --drivers="aufs" \
       --nomdadmconf \
       --nolvmconf \
       --show-modules \
       --strip \
       --local \
       $initramfs_pathname $kernel_version

]

capture: [
#!/bin/bash

die() {
	echo $*
	rm -f $[path/mirror/target]
	exit 1
}

trap "die user interrupt - Removing incomplete template..." INT

rm -rf /tmp/steps || die "Steps cleanup fail"
outdir=`dirname $[path/mirror/target]`
if [ ! -d $outdir ]
then
	install -d $outdir || "Output path $outdir does not exist"
fi

echo "Creating $[path/mirror/target]..."

kernel_pathname="$(find $[path/chroot/stage]/boot/ -name 'kernel*' -type f | head -n 1)"
initramfs_pathname="${kernel_pathname/kernel-/initramfs-}"

cp $initramfs_pathname $[path/mirror/target]
cp $initramfs_pathname $outdir/initramfs

if [ $? -ge 2 ]
then
	die "Error creating tarball"
fi

]

[section portage]

ROOT: /