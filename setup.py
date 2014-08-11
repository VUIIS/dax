#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" setup.py

Packaging for dax
"""

import os
from setuptools import setup, find_packages

def get_version():
    basedir = os.path.dirname(__file__)
    with open(os.path.join(basedir, 'dax/version.py')) as f:
        VERSION = None
        exec(f.read())
        return VERSION
    raise RuntimeError("No version found")

def readme():
    with open('README.rst.example') as f:
        return f.read()

if __name__ == '__main__':
    setup(name='dax',
          version=get_version(),
          description='A python API for VUIIS CCI Infrastructure',
          url='http://github.com/VUIIS/dax',
          author='VUIIS CCI',
          author_email='vuiis-cci@googlegroups.com',
          license='MIT',
          packages=find_packages(),
          package_data={},
          test_suite='nose.collector',
          tests_require=['nose'],
          install_requires=['pycap'],
          dependency_links=['git+git://github.com/bud42/pyxnat.git@b4917ba#egg=pyxnat.git'],
          zip_safe=True,
          scripts=[
                   'bin/dax_update', 
                   'bin/dax_update_open_tasks', 
                   'bin/dax_upload',
                   'bin/dax_lastupdated_subj2sess',
                   ],
          classifiers=[
                       # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
                       # "Development Status :: 1 - Planning",
                       # "Development Status :: 2 - Pre-Alpha",
                       "Development Status :: 3 - Alpha",
                       # "Development Status :: 4 - Beta",
                       # "Development Status :: 5 - Production/Stable",
                       # "Development Status :: 6 - Mature",
                       # "Development Status :: 7 - Inactive",
                       "Environment :: Console",
                       "Intended Audience :: Science/Research",
                       "Operating System :: MacOS :: MacOS X",
                       "Operating System :: POSIX",
                       "Operating System :: POSIX :: Linux",
                       "Operating System :: Unix",
                       "Programming Language :: Python :: 2.6",
                       "Programming Language :: Python :: 2.7",
                       "Programming Language :: Python :: 2 :: Only",
                       "Topic :: Scientific/Engineering",
                       "Topic :: Scientific/Engineering :: Information Analysis",
                       ],
          )
