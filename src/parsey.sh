#!/bin/sh
old_dir=$(pwd)
cd ../../parsey-mcparseface/src/models/syntaxnet/
echo Input 1: $1
echo $1 | ./syntaxnet/demo.sh
cd $old_dir

