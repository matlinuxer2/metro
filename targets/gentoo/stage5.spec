[collect ./stage/common.spec]
[collect ./stage/capture/squashfs.spec]

[section path/mirror]

source: $[:source/subpath]/$[source/name].tar.*

[section source]
: stage4
version: << $[path/mirror/control]/version/$[]
name: $[]-$[:subarch]-$[:version]

build: $[target/build]
subarch: $[target/subarch]


[section path/mirror]

target: $[:source/subpath]/$[target/name].squashfs

[section target]

name: stage5-$[target/subarch]-$[:version]

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]
USE=-dynamic emerge $eopts cryptsetup || exit 1
genkernel --unionfs --lvm --dmraid --luks all || exit 1
cat << EOF >>/bin/bashlogin || exit 1
#!/bin/sh

export HOME=/root
cat /etc/motd 2>/dev/null
cd /root
[[ -e .bash_profile ]] && source .bash_profile
exec -l /bin/bash -i
EOF
sed -i -e '/^c/s!agetty!agetty -nl /bin/bashlogin!' /etc/inittab || exit 1
]

[section portage]

ROOT: /
