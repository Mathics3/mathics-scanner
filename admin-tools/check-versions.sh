#!/bin/bash
function finish {
  cd $mathics_scanner_owd
}

# FIXME put some of the below in a common routine
mathics_scanner_owd=$(pwd)
trap finish EXIT

cd $(dirname ${BASH_SOURCE[0]})
if ! source ./pyenv-versions ; then
    exit $?
fi

cd ..
for version in $PYVERSIONS; do
    echo --- $version ---
    if ! pyenv local $version ; then
	exit $?
    fi
    make clean && pip install -e .
    make
    if ! make check; then
	exit $?
    fi
    echo === $version ===
done
finish
