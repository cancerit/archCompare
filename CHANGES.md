# CHANGES

## 2.0.0
* added json config  file as required parameter
* added cleanup option
* All `diffs` compariosons will be now handled by user defined json file
* User can request multiple comparsions on command line
* Output format now contains results for all requested comparsons


## 1.1.4

* Remove `logging` from install_requires as it breaks python3 install
* Change travis to use `pip install .` rather than installing dependencies

## 1.1.3

* regex made compatible with python 3.5 and 3.6

## 1.1.2

* added # to header line
* modified setup.sh to add beautiful tables in bithinstall and setup_require section for CI and pip installation
