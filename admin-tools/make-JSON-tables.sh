#!/bin/bash
# Create a complete set of JSON tables.
bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
PYTHON=${PYTHON:-python}

cd $mydir/../mathics_scanner/data

# The below is not needed. But it reminds us that the code
# below is importing mathics_scanner imports in a different way
# that assumes it is okay for JSON tables not to appear.
export MATHICS3_TABLE_GENERATION="true"

$PYTHON ../generate/boxing_characters.py -o boxing-characters.json
$PYTHON ../generate/named_characters.py -o named-characters.json
$PYTHON ../generate/operators.py -o operators.json
