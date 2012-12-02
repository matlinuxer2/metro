[section trigger]

ok/symlink: [
#!/bin/bash
ln -sf $[path/mirror/target/link/dest] $[path/mirror/target/link] || exit 3
# support another symlink, whose location is defined by "auxlink" in the layout.conf:
auxlink=$[path/mirror/target/auxlink:zap]
auxlinkdest=$[path/mirror/target/auxlinkdest:zap]
if [ -n "${auxlink}${auxlinkdest}" ]; then
	# this variable defines a list of targets to enable auxlink for:
	tle=$[path/mirror/target/auxlink/enable:zap]
	found=""
	for t in $tle; do
		[ "$t" = "$[target]" ] && found="yes"
	done
	# create link if "enable" var tells us to:
	if [ "$found" = "yes" ]; then
		install -d $(dirname $auxlink) || exit 4
		ln -sf "$auxlinkdest" "$auxlink" || exit 5
	fi
fi
]
