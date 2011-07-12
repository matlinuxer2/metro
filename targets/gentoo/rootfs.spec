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

eselect profile set 1

emerge $eopts --getbinpkg=y --usepkg=y \
        sys-kernel/genkernel \
	|| (bash ; exit 1 )

### To patch genkernel here
vim -i NONE -e -X -c ':123 move 117' -c':wq' $(which genkernel)

genkernel --no-clean --no-mountboot \
        --no-kernel-sources \
	--kerncache=/tmp/kerncache.tar.bz2 \
	kernel

keywords_file="/usr/portage/_etc/package.keywords"
use_file="/usr/portage/_etc/package.use"
if [ -e "$keywords_file" ]; then
        echo "Coping portage settings $keywords_file => /etc/portage/package.keywords ..."
        cp -v $keywords_file /etc/portage/package.keywords 
fi
if [ -e "$use_file" ]; then
        echo "Coping portage settings $use_file => /etc/portage/package.use ..."
        cp -v $use_file /etc/portage/package.use 
fi

cat >> /etc/portage/package.keywords <<EOF
$[[emerge/packages/rootfs_keywords]]
EOF

cat >> /etc/portage/package.use <<EOF
$[[emerge/packages/rootfs_use]]
EOF

export USE="$[portage/USE] bindist"
emerge $eopts $[emerge/packages/rootfs:zap] || ( bash ; exit 1 )

emerge $eopts --oneshot net-dialup/mingetty

sed -i -e '/^c/s!agetty 38400!mingetty --autologin root --noclear!' /etc/inittab || exit 1

]

[section portage]

ROOT: /
