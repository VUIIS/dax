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
          description='Distributed Automation for XNAT',
          url='http://github.com/VUIIS/dax',
          author='VUIIS CCI',
          author_email='vuiis-cci@googlegroups.com',
          license='MIT',
          packages=find_packages(),
          package_data={},
          test_suite='nose.collector',
          tests_require=['nose'],
          install_requires=['pycap','lxml','pyxnat', 'httplib2'],
          zip_safe=True,
          scripts=[
                   'bin/dax_tools/dax_manager', 
                   'bin/dax_tools/dax_build',
                   'bin/dax_tools/dax_launch',
                   'bin/dax_tools/dax_update_tasks', 
                   'bin/dax_tools/dax_upload',
                   'bin/dax_tools/run_spider',
                   'bin/dax_tools/GenerateModuleTemplate',
                   'bin/dax_tools/GenerateProcessorTemplate',
                   'bin/dax_tools/GenerateSpiderTemplate',
                   'bin/dax_tools/GenerateSettingsTemplate',
                   'bin/freesurfer_tools/fsupload',
                   'bin/freesurfer_tools/fsdownload',
                   'bin/freesurfer_tools/fsview',
                   'bin/Xnat_tools/Redcapreport',
                   'bin/Xnat_tools/Xnatcheck',
                   'bin/Xnat_tools/Xnatdownload',
                   'bin/Xnat_tools/XnatDemographic',
                   'bin/Xnat_tools/Xnatinfo',
                   'bin/Xnat_tools/Xnatmirror',
                   'bin/Xnat_tools/XnatNDAR',
                   'bin/Xnat_tools/Xnatquery',
                   'bin/Xnat_tools/Xnatreport',
                   'bin/Xnat_tools/Xnatsessionupdate',
                   'bin/Xnat_tools/XnatCheckLogin',
                   'bin/Xnat_tools/XnatSwitchProcessStatus',
                   'bin/Xnat_tools/Xnatupload',
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
