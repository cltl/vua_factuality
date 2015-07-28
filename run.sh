#!/bin/bash

###local settings for when this is run as part of the newsreader vm. Adapt paths where appropriate
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export PYTHONPATH=$PYTHONPATH:/home/newsreader/opt/lib/python2.7/
export PATH=$PATH:.
root=/home/newsreader/components/VUA-factuality.v30
tmpDir=$(mktemp -d --tmpdir=$root)

#cd $root
/home/newsreader/opt/bin/python $root/vua_factuality_naf_wrapper.py -t ~/opt/bin/timbl -p $root/ $tmpDir/

rm -rf $tmpDir >& /dev/null

