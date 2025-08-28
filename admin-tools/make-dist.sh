#!/bin/bash
PACKAGE=mathics-scanner

# FIXME put some of the below in a common routine
function finish {
  cd $mathics_scanner_owd
}

cd $(dirname ${BASH_SOURCE[0]})
mathics_scanner_owd=$(pwd)
trap finish EXIT

if ! source ./pyenv-versions ; then
    exit $?
fi

cd ..
source mathics_scanner/version.py
echo $__version__

python setup.py bdist_wheel
python ./setup.py sdist
finish
