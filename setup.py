#!/usr/bin/env python

import os

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

with open(os.path.join(os.path.dirname(__file__), 'requirements.in')) as requirements:
    REQUIREMENTS = requirements.readlines()

REQUIREMENTS_LINK = [req.split()[1] for req in REQUIREMENTS if '://' in req]
REQUIREMENTS_PYPI = [req for req in REQUIREMENTS if '://' not in req]

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='cagnottesolidaire',
    version='1.0.0',
    packages=['cagnottesolidaire'],
    install_requires=REQUIREMENTS_PYPI,
    dependency_links=REQUIREMENTS_LINK,
    include_package_data=True,
    license='GPL License',
    description='A social crowdfunding app',
    long_description=README,
    url='https://caracole.io/cagnottesolidaire/',
    author='Guilhem Saurel',
    author_email='webmaster@saurel.me',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
