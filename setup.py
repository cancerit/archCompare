#!/usr/bin/env python3

from setuptools import setup

config = {
    'version': '2.1.0',
    'name': 'archCompare',
    'description': 'tool to comapre files and/or archives',
    'author': 'Shriram G Bhosle',
    'url': 'https://github.com/CancerIT/archCompare',
    'author_email': 'cgphelp@sanger.ac.uk',
    'python_requires': '>= 3.3',
    'setup_requires': ['pytest', 'pytest-cov'],
    'install_requires': ['beautifultable'],
    'packages': ['archCompare'],
    'package_data': {'archCompare': ['../examples/*.json', 'config/*.conf']},
    'entry_points': {
        'console_scripts': ['cgpCompare=archCompare.compare_command:main'],
    }
}

setup(**config)
