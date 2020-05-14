Installing DAX in a Virtual Environment
=======================================

Table of Contents
~~~~~~~~~~~~~~~~~

1.  `Requirements <#requirements>`__
2.  `Setup <#setup>`__
  1.  `OS X Setup <#os-x-setup>`__
  2.  `Ubuntu Setup <#ubuntu-setup>`__
3.  `Create the Virtual Environment <#create-the-virtual-environment>`__
  1.  `Anaconda <#anaconda>`__
  2.  `VirtualEnv <#virtualenv>`__
4.  `Install DAX <#install-dax>`__
5.  `Verify Installation <#verify-installation>`__
6. `Installing Specific Versions of DAX <#installing-specific-versions-of-dax>`__

------------
Requirements
------------
There are a few things required for DAX to work properly.

* Python3
* pip3
* A virtual environment

-----
Setup
-----

OS X Setup
~~~~~~~~~~

Python 2 is installed already as part of OS X. We need to install Python 3 as well. Visit https://www.python.org/downloads/ to download and install the latest version. To verify Python 3 has been installed correctly:

:: 

	python3 --version
	
The output should be similar to:

::

	Python 3.8.3

The install directory can also be verified:

::

	which python3

Once Python 3 is installed, pip3 can be installed by running the following:

::

	python3 get-pip.py

And can be similarly verified by:

::

	which pip3
	
There are a few virtual environments that can be used, but to install virtualenv:

::

	pip install virtualenv

Ubuntu Setup
~~~~~~~~~~~~

::

	$ sudo apt install python pip virtualenv

------------------------------
Create the Virtual Environment
------------------------------
DAX is to be installed only on virtual environments (anaconda, virtualenv, etc) on Python-3.6. 

Anaconda
~~~~~~~~

Install instructions here: https://docs.anaconda.com/anaconda/install/

VirtualEnv
~~~~~~~~~~

https://virtualenv.pypa.io/en/latest/installation.html

To setup your virtual environment, do the following

::

	python3.6 -m virtualenv venv/dax
	source venv/dax/bin/activate

If this ran properly there should be a "(dax)" in the front of your terminal prompt. The activate command can be added to e.g. `.bash_profile`.

-----------
Install DAX
-----------

Once the virtual environment with Python3.6 is created, dax can be installed by using

::

	pip3 install dax
	dax setup
	XnatCheckLogin --host <xnat_host_url>
	# When prompted, enter user/pwd combination
	# Yes to use as default host

Note that sudo is NOT required when you are in the virtual environment.

-------------------
Verify Installation
-------------------

::

	(dax) $ python
	>>> import dax

If everything ran properly, then the import should work without error.

-----------------------------------
Installing Specific Versions of DAX
-----------------------------------

To install a specific version of DAX by its tag in the github repository (this example is for 1.0.0)

::

	pip install git+https://github.com/VUIIS/dax.git@v1.0.0


