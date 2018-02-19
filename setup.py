# coding: utf-8

"""A setuptools based setup module for pip usage.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get version
with open(path.join(here, '__version__'), encoding='utf-8') as f:
    __version__ = f.read().strip()

SETUP_KW_ARGS = {
    'name': 'spin_store',  # Required
    'version': __version__,     # Required
    'description': 'django example application',
    'long_description': long_description,
    'url': 'https://github.com/alfa-sw/spin_store',
    'author': 'giovanni angeli',
    'author_email': 'giovanniangeli@alfadispenser.com',
    'classifiers': [  # Optional
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        # ~ 'Programming Language :: Python :: 2',
        # ~ 'Programming Language :: Python :: 2.7',
        # ~ 'Programming Language :: Python :: 3',
        # ~ 'Programming Language :: Python :: 3.4',
    ],
    'packages': find_packages(exclude=['docs', 'tests', 'tmp']),  # Required
    'install_requires': [
        "Django",           #==1.11
        "django-suit",      #==0.2.25
        "jsonschema",       #==2.6.0
        # ~ "nose2",            #==0.7.3
        # ~ "pytz",             #==2017.3
    ],
    
    'include_package_data': True,    # include everything in source control
    'exclude_package_data': {'*': ['__pycache__']},
    
    'package_data': { 
        'spin_store': [
            '__version__', 
            'frontend'
        ],
    },
    'entry_points': {  # Optional
        'console_scripts': [
            'spin_store=spin_store:main',
        ],
    },
}


if __name__ == "__main__":
    setup(**SETUP_KW_ARGS)
