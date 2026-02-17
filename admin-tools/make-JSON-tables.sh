#!/bin/bash
# Create a complete set of JSON tables.
bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
PYTHON=${PYTHON:-python}

cd $mydir/../mathics_scanner/data
$PYTHON ../generate/boxing_characters.py -o boxing-characters.json
$PYTHON ../generate/named_characters.py -o named-characters.json
$PYTHON ../generate/operators.py -o operators.json
