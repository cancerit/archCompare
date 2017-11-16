#!/usr/bin/env python3

from setuptools import setup

config = {
    'version': '1.1.3',
    'name': 'archCompare',
    'description': 'tool to comapre files and/or archives',
    'author': 'Shriram G Bhosle',
    'url': 'https://github.com/CancerIT/archCompare',
    'author_email': 'cgphelp@sanger.ac.uk',
    'python_requires': '>= 3.3',	
    'setup_requires': ['pytest','pytest-cov'],
    'install_requires': ['logging','beautifultable'],
    'packages': ['archCompare'],
    'package_data': {'archCompare': ['config/*.json','config/*.conf']},
    'entry_points': {
        'console_scripts': ['cgpCompare=archCompare.compare_command:main'],
    }
}

setup(**config)
