#!/usr/bin/env python3

from setuptools import setup

config = {
    'name': 'archCompare',
    'description': 'tool to comapre files and/or archives',
    'author': 'Shriram G Bhosle',
    'url': 'https://github.com/CancerIT/archCompare',
    'download_url': 'Whereto download it.',
    'author_email': 'cgphelp@sanger.ac.uk',
    'version': '1.0.0',
    'python_requires': '>= 3.3',	
    'setup_requires': ['pytest','pytest-cov'],
    'install_requires': ['logging'],
    'packages': ['archCompare'],
    'package_data': {'archCompare': ['config/*.json','config/*.conf']},
    'entry_points': {
        'console_scripts': ['cgpCompare=archCompare.compare_command:main'],
    }
}

setup(**config)
