[collect ./source/stage3.spec]
[collect ./target/stage4.spec]

[section stage4]

target/name: kernel

[section steps]
unpack/post: [
#!/bin/bash

conf="$[path/mirror/snapshot/subpath]/kernel-config"

if [ -e "$conf" ]; then
	[ ! -d $[path/chroot]/boot ] && install -d $[path/chroot]/boot --mode=0755
	echo "Coping Linux kernel config $conf..."
	cp  $conf $[path/chroot]/tmp/kernel-config
else
	echo "Required file $conf not found. Build kernel with default settings..." 
fi

]

chroot/run: [
#!/bin/bash
$[[steps/setup]]

cat > /etc/portage/package.keywords <<EOF
sys-apps/sysvinit ~*
sys-apps/aufs2 ~*
EOF

cat > /etc/portage/package.use<<EOF
dev-libs/libgcrypt static-libs
sys-fs/aufs2 kernel-patch
EOF

emerge $eopts --getbinpkg=y --usepkg=y \
      	sys-kernel/gentoo-sources \
        sys-kernel/genkernel \
	|| (bash ; exit 1 )

if [ -f "/tmp/kernel-config" ]; then
	opts_config=" --kernel-config=/tmp/kernel-config "
fi

genkernel --no-clean --no-mountboot \
	$opts_config \
	kernel

DRV_PKGS="sys-fs/aufs2 app-emulation/kqemu"
emerge --oneshot --autounmask-write $DRV_PKGS
emerge --oneshot --autounmask-write $DRV_PKGS

genkernel --no-clean --no-mountboot \
	--kerncache=/boot/$[target/name].tar.bz2 \
	$opts_config \
	kernel
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

cp $[path/chroot/stage]/boot/$[target/name].tar.bz2 $[path/mirror/target]

kernel_pathname="$(find $[path/chroot/stage]/boot/ -name 'kernel*' -type f | head -n 1)"

cp $kernel_pathname $outdir/kernel
cp $[path/chroot/stage]/usr/src/linux/.config $outdir/config

if [ $? -ge 2 ]
then
	die "Error creating tarball"
fi
]

[section portage]

ROOT: /
