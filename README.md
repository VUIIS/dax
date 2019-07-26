![](https://github.com/VUIIS/dax/blob/master/docs/images/dax_logo.png)
Distributed Automation for XNAT
===

# Install DAX

Install it with:

~~~~~~~~
pip install dax
~~~~~~~~

Use --upgrade to overwrite previous installation

To install current master:
~~~~~~~~
sudo apt-get install -y zlib1g-dev libxft-dev
sudo apt-get install -y libjpeg-dev
sudo apt-get install libxml2-dev libxslt1-dev
sudo apt-get install libfreetype6-dev
sudo apt-get install libffi-dev
sudo apt-get install libssl-dev
sudo apt-get install libatlas-base-dev gfortran
pip install git+https://github.com/VUIIS/dax.git --upgrade
~~~~~~~~

or in a docker:
~~~~~~~~
#
# This sets up a base dax docker image
#
FROM ubuntu:14.04
# Install updates, pip and dax
RUN \
apt-get update && \
apt-get -y install python-pip libxft-dev && \
apt-get -y install libxml2-dev libxslt1-dev python-dev zlib1g-dev && \
apt-get -y install zlib1g-dev && \
apt-get -y install libjpeg-dev && \
apt-get -y install libxml2-dev libxslt1-dev && \
apt-get -y install libfreetype6-dev && \
apt-get -y install libffi-dev && \
apt-get -y install libssl-dev && \
apt-get -y install libatlas-base-dev gfortran git && \
pip install dax

#Set to bash
CMD ["bash"]
~~~~~~~~

or a specific branch:

~~~~~~~~
pip install git+https://github.com/VUIIS/dax.git@branch_name --upgrade
~~~~~~~~

# Docs
[![Documentation Status](https://readthedocs.org/projects/dax/badge/?version=master)](http://dax.readthedocs.org/en/master/?badge=master)

<!-- Disabled since masijenkins is no longer in use for this purpose 
# Build
[![Build Status](http://masijenkins.vuse.vanderbilt.edu:8080/buildStatus/icon?job=Build_DAX)](http://masijenkins.vuse.vanderbilt.edu:8080/job/Build_DAX/)
-->

<!-- Disabled since spiders are now repos on github
# Spiders
All of our piplines are available on NITRC. [Come join our team!](https://www.nitrc.org/projects/masimatlab)
-->
