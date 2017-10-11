#!/usr/bin/env bash
 
set -e
pytest\
 --cov-report term\
 --cov-report html\
 --cov-fail-under=50\
 --cov=archCompare\
 -vv\

#echo -e "\n#################\n# Running pylint:\n"
#env/bin/pylint --output-format=colorized bin/*.py archCompare
#echo -e "#\n#################"
#exit 0 # don't die based on pylint
