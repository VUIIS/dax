#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" setup.py

Packaging for dax
"""

from glob import glob
import os
from setuptools import setup, find_packages
import shutil


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


description = 'Distributed Automation for XNAT'

# Note: this long_description is actually a copy/paste from the top-level
# README.txt, so that it shows up nicely on PyPI.  So please remember to edit
# it only in one place and sync it correctly.
long_description = """
========================================================
DAX: Distributed Automation for XNAT
========================================================

*DAX*, is  a python package developed at Vanderbilt University, Nashville, TN,
USA. It's available on github at the address: https://github.com/VUIIS/dax.
See the different tutorials bellow to learn more about this package and how
to use it.

XNAT gives an incredible flexible imaging informatics software platform to
organise, manage any imaging data. It also provides a Pipeline Engine to run
processings on your data. The pipeline engines has an important learning curve
and doesn't provide a way to run processes when your XNAT instance isn't
connected to your cluster.

*DAX*, an open-source initiative under the umbrella of Vanderbilt University
Institute of Imaging Science (VUIIS), is a Python project that provides a
uniform interface to run pipelines on a cluster by grabbing data from a XNAT
database via RESTApi Calls.

*DAX* allows you to:

* extract information from XNAT via scripts (bin/Xnat_tools/Xnat...)
* create pipelines (spiders/processors) to run pipelines on your data
* build a project on XNAT with pipelines (assessors)
* launch pipelines on your cluster and upload results back to xnat
* interact with XNAT via python using commands in XnatUtils.
"""

NAME = 'dax'
MAINTAINER = 'VUIIS CCI'
MAINTAINER_EMAIL = 'vuiis-cci@googlegroups.com'
DESCRIPTION = description
LONG_DESCRIPTION = long_description
URL = "http://github.com/VUIIS/dax"
DOWNLOAD_URL = "http://github.com/VUIIS/dax"
LICENSE = 'MIT'
CLASSIFIERS = [
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
    "Topic :: Scientific/Engineering :: Information Analysis"]
AUTHOR = MAINTAINER
AUTHOR_EMAIL = MAINTAINER_EMAIL
PLATFORMS = ["MacOs",
             "Linux"]
VERSION = get_version()
PROVIDES = ['niftypipe']

# versions
SPHINX_MIN_VERSION = '1.4'
NIBABEL_MIN_VERSION = '2.0.1'
NUMPY_MIN_VERSION = '1.6.2'
MATPLOTLIB_MIN_VERSION = '1.4.3'


REQUIRES = [
    'Sphinx>=%s' % SPHINX_MIN_VERSION,
    'nibabel>=%s' % NIBABEL_MIN_VERSION,
    'numpy>=%s' % NUMPY_MIN_VERSION,
    'matplotlib>=%s' % MATPLOTLIB_MIN_VERSION,
    'pycap',
    'pyxnat',
    'pyyaml',
    'scipy',
    'lxml',
    'xlrd',
    'pillow',
    'pydicom',
    'httplib2',
    'future',
    'configparser'
]

TESTS_REQUIRES = ['nose']


if __name__ == '__main__':
    if not os.path.exists(os.path.join(os.path.expanduser('~'),
                                       '.dax_settings.ini')):
        shutil.copy('dax/dax_settings.ini',
                    os.path.join(os.path.expanduser('~'), '.dax_settings.ini'))

    setup(name=NAME,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          version=get_version(),
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          url=URL,
          download_url=DOWNLOAD_URL,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          platforms=PLATFORMS,
          license=LICENSE,
          packages=find_packages(),
          package_data={},
          test_suite='nose.collector',
          tests_require=TESTS_REQUIRES,
          install_requires=REQUIRES,
          zip_safe=True,
          scripts=glob(os.path.join('bin', '*', '*')),
          classifiers=CLASSIFIERS)
