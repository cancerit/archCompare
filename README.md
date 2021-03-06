# archComapre

| Master                                              | Develop                                               |
| --------------------------------------------------- | ----------------------------------------------------- |
| [![Master Badge][travis-master-badge]][travis-repo] | [![Develop Badge][travis-develop-badge]][travis-repo] |

This tool compares a pair of data structures [ files, directories and archives ]
Provides concise information about the archive content using tools defined in the config file.

<!-- TOC depthFrom:2 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Design](#design)
- [Tools](#tools)
	- [cgpCompare](#cgpcompare)
- [INSTALL](#install)
	- [Package Dependencies](#package-dependencies)
- [Development environment](#development-environment)
	- [Development Dependencies](#development-dependencies)
		- [Setup VirtualEnv](#setup-virtualenv)
- [Cutting a release](#cutting-a-release)
	- [Install via `.whl` (wheel)](#install-via-whl-wheel)
- [LICENCE](#licence)
<!-- /TOC -->

## Design

Many components of this system are heavily driven by configuration files.  This
is to allow new validation code to be added and incorporated without modifying
the driver code.

## Tools

`cgpCompare` has multiple commands, listed with `cgpCompare --help`.

### cgpCompare

Takes the input archives, files, folders and does the comparison for matching file types based on tools defined in `json` configuration file.
Please refer `examples/sample_config.json` file to construct a config file or one can use this file to add custom tools.
Warning:Please make sure all the tools referred in the diffs section of your `json` file are present in the user's environment

Valid input types include:

* .tar - archive containing multiple files and folders to compare
* folder - any folder containing sub folders and files
* file - any file with extension configured in the user's `json` configuration file

Default output is exit status 0; if verbose option set then tab separated columns containing:

* `File_a`  - compared file name  from first archive
* `File_b`  - compared file name  from second archive
* `<reportsOn columns>` - if files are compared and found similar it will have one of the value [ PASS=similar, FAIL=different, NA=Not Applicable OR <ReasonForNoComparison> ]

Various exceptions can occur for malformed files and will  be reported in log file

## INSTALL

Installing via `pip install` .Simply execute with the path to the compiled 'whl' found on the [release page][archCompare-releases]:

```bash
pip install archCompare.X.X.X-py3-none-any.whl
```

Release `.whl` files are generated as part of the release process and can be found on the [release page][archCompare-releases] **(version >= 1.1.4)**.

### Package Dependencies

`pip` will install the relevant dependancies, listed here for convenience:

* [beautiful-table]

## Development environment

This project uses git pre-commit hooks. As these will execute on your system it
is entirely up to you if you activate them.

If you want tests, coverage reports and lint-ing to automatically execute before
a commit you can activate them by running:

```bash
git config core.hooksPath git-hooks
```

Only a test failure will block a commit, lint-ing is not enforced (but please consider
following the guidance).

You can run the same checks manually without a commit by executing the following
in the base of the clone, ensure you have the test packages listed in [Development Dependencies](#development-dependencies):

```bash
./run_tests.sh
```

### Development Dependencies

#### Setup VirtualEnv

```bash
cd $PROJECTROOT
hash virtualenv || pip3 install virtualenv
virtualenv -p python3 env
source env/bin/activate
python setup.py develop # so bin scripts can find module
```

For testing/coverage (`./run_tests.sh`)

```bash
source env/bin/activate # if not already in env
pip install pytest
pip install pytest-cov
```

__Also see__ [Package Dependencies](#package-dependencies)

## Cutting a release

__Make sure the version is incremented__ in `./setup.py`

### Install via `.whl` (wheel)

Generate `.whl`

```bash
source env/bin/activate # if not already
python setup.py bdist_wheel -d dist
```

Install .whl

```bash
# this creates an wheel archive which can be copied to a deployment location, e.g.
scp dist/archCompare.X.X.X-py3-none-any.whl user@host:~/wheels
# on host
pip install --find-links=~/wheels archCompare
```

<!-- References -->
[beautiful-table]: https://pypi.python.org/pypi/beautifultable/
[archCompare-releases]: https://github.com/cancerit/archCompare/releases
[travis-master-badge]: https://travis-ci.org/cancerit/archCompare.svg?branch=master
[travis-develop-badge]: https://travis-ci.org/cancerit/archCompare.svg?branch=develop
[travis-repo]: https://travis-ci.org/cancerit/archCompare

## LICENCE

Copyright (c) 2017 Genome Research Ltd.

Author: Cancer Ageing and Somatic Mutation <cgphelp@sanger.ac.uk>

This file is part of cgpCompare.

cgpCompare is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
