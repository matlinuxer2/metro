[section steps]

capture: [
#!/bin/bash
outdir=`dirname $[path/mirror/target]`
if [ ! -d $outdir ]
then
	install -d $outdir || exit 1
fi
squashout="$[path/mirror/target]"
squashout="${squashout%.*}.squashfs"
mksquashfs $[path/chroot/stage] $squashout
chmod a+r $squashout
if [ $? -ge 2 ]
then
	rm -f "$squashout" "$[path/mirror/target]"
	exit 1
fi
if [ $? -ne 0 ]
then
	echo "Compression error - aborting."
	rm -f $[path/mirror/target]
	exit 99
fi
]


