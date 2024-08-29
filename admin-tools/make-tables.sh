#!/bin/bash
# Create a complete set of tables.
# This just runs build_tables.py in this distribution
bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
PYTHON=${PYTHON:-python}

cd $mydir/../mathics_scanner/data
$PYTHON ../generate/build_tables.py -o characters.json
$PYTHON ../generate/build_operator_tables.py -o operators.json
