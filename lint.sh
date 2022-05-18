#!/bin/bash
pylint=0
yamllint=0

if [ ! $CI ]
then
	echo "Auto-formatting python"
	python -m autopep8 --in-place --recursive .

    echo "Linting python"
    python -m pylint ./*.py --disable=W0511
fi

if [ $CI ]
then
    echo "Linting python"
    python -m pylint ./*.py --disable=W0511,E0401
    if [ $? -ne 0 ]
    then
    	pylint=1
    	echo "Linting python failed"
    fi
fi

if [ $pylint -ne 0 ]
then
	exit 1
fi