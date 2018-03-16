#!/usr/bin/env python

import os

from setuptools import setup

readme_file = os.path.join(os.path.dirname(__file__), 'README.rst')
if not os.path.isfile(readme_file):
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
with open(readme_file) as readme:
    README = readme.read()

with open(os.path.join(os.path.dirname(__file__), 'requirements.in')) as requirements:
    REQUIREMENTS = [req.split('#egg=')[1] if '#egg=' in req else req for req in requirements.readlines()]


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='cagnottesolidaire',
    version='2.0.0',
    packages=['cagnottesolidaire'],
    install_requires=REQUIREMENTS,
    include_package_data=True,
    license='BSD',
    description='A social crowdfunding app',
    long_description=README,
    url='https://github.com/caracole-io/cagnottesolidaire/',
    author='Guilhem Saurel',
    author_email='webmaster@caracole.io',
    python_requires='>=3.6',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
