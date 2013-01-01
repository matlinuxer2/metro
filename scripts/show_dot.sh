#!/usr/bin/env bash

#
# Author: Chun-Yu Lee (Mat) <matlinuxer2@gmail.com>
#

# just run command below:
#   bash ./show_dot.sh  | grep -v '\$' | dot -Tpng > ./struct.png 


ROOT=$( dirname $( readlink -f $0) )
prefix=$( readlink -f $ROOT/../targets/gentoo/ )

function pipe_in_python() {

python -c "$(cat <<EOPY
import sys
import re
import os

prefix_str="$prefix"

for line in sys.stdin:
        #print line
	pattern = "(.*):\[collect (.*)]"
	result = re.findall( pattern, line)
	from1 = result[0][0]
	to1 = result[0][1]
	
	d = os.path.dirname( from1 )
	to2 = os.path.join( d, to1 )
	to3 = os.path.realpath( to2 )
	
	from4 = from1.replace( prefix_str, "")
	to4 = to3.replace( prefix_str, "")

	print "\"%s\" -> \"%s\" ; " % ( from4, to4 )
	
EOPY
)"

}

function pipe_in_python2() {

python -c "$(cat <<EOPY
import sys
import re
import os

prefix_str="$prefix"

for line in sys.stdin:
	node = line.replace( prefix_str, "").strip()
	print " \"%s\" ; " % ( node )
	
EOPY
)"

}


echo "digraph metro { "
echo " rankdir=LR ; "
echo " nodesep=1 ; "
echo " ranksep=3                                                                                           ; "

echo "  subgraph source { "
echo "          node [style=filled,color=blue];"
find $prefix -type f -name '*.spec' | grep 'gentoo/target' | pipe_in_python2 
echo "  } "

echo "  subgraph source { "
echo "          node [style=filled,color=green];"
find $prefix -type f -name '*.spec' | grep 'gentoo/step' | pipe_in_python2 
echo "  } "

echo "  subgraph source { "
echo "          node [style=filled,color=yellow];"
find $prefix -type f -name '*.spec' | grep 'gentoo/source' | pipe_in_python2 
echo "  } "


grep "collect" -Hr $prefix | pipe_in_python | sort -k 3 | uniq 

echo " } "
