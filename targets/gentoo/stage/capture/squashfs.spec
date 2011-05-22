[section steps]

capture: [
#!/bin/bash
outdir=`dirname $[path/mirror/target]`
if [ ! -d $outdir ]
then
	install -d $outdir || exit 1
fi
sqfsout="$[path/mirror/target]"
sqfsout="${sqfsout%.*}.squashfs"
mksquashfs $[path/chroot/stage] $sqfsout
if [ $? -ge 2 ]
then
	rm -f "$sqfsout" "$[path/mirror/target]"
	exit 1
fi
if [ $? -ne 0 ]
then
	echo "Compression error - aborting."
	rm -f $[path/mirror/target]
	exit 99
fi
]

