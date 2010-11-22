[collect ./stage/common.spec]
[collect ./stage/capture/squashfs.spec]
[collect ./stage/stage3-derivative.spec]

[section path/mirror]

target: $[:source/subpath]/$[target/name].squashfs

[section target]

name: stage5-$[target/subarch]-$[:version]

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
USE=-dynamic emerge $eopts cryptsetup || exit 1
genkernel --lvm --dmraid --luks all || exit 1
sed -i -e '/^c/s!agetty 38400!mingetty --autologin root --noclear !' \
	/etc/inittab || exit 1
cat <<EOF >>/etc/login.defs
NO_PASSWORD_CONSOLE tty1:tty2:tty3:tty4:tty5:tty6
EOF
echo > /etc/fstab || exit 1
]

[section portage]

ROOT: /
