#!/bin/bash
CURDIR=`dirname $0`
OUTPUT=$CURDIR/output
SRC="imagesaver.py s3provider test.py"

exec_cmd(){
    echo "exec $1"
    `$1`
}
if [ -d $OUTPUT ]
then
    exec_cmd "rm -rf $OUTPUT"
fi
exec_cmd "mkdir -p $OUTPUT"

exec_cmd "cp -r $SRC $OUTPUT"
echo "ok"

