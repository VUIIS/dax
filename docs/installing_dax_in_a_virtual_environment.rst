Installing DAX in a Virtual Environment
=======================================

Table of Contents
~~~~~~~~~~~~~~~~~

1.  `Setup <#setup>`__
2.  `OS X Setup <#os-x-setup>`__
3.  `Ubuntu Setup <#ubuntu-setup>`__
4.  `Create the Virtual Environment <#create-the-virtual-environment>`__
5.  `Install DAX <#install-dax>`__
6.  `Post Install <#post-install>`__
7.  `OS X Post Install <#os-x-post-install>`__
8.  `Ubuntu Post Install <#ubuntu-post-install>`__
9.  `Verify Installation <#verify-installation>`__
10. `Installing Specific Versions of DAX`__
11. `Alternative Installation (non-pip) <#alternative-installation-(non-pip)>`__

-----
Setup
-----

OS X Setup
~~~~~~~~~~

Python is installed already as part of OS X.

::

	sudo easy_install pip
	pip install virtualenv

Ubuntu Setup
~~~~~~~~~~~~

::

	$ sudo apt install python pip virtualenv

------------------------------
Create the Virtual Environment
------------------------------

In production accounts, dax is to be installed only on virtual environments (anaconda, virtualenv, etc) on Python-3.6. Current DAX virtual environment is in

::

	/data/mcr/centos7/venv/dax-1.0

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
	XnatCheckLogin --host http://129.59.135.143:8080/xnat
	# When prompted, enter user/pwd combination
	# Yes to use as default host

Alternately, all dependencies and dax are listed in the SOP document and they can be installed to the virtual environment by making a text file and using it like

::

	pip install -r

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

----------------------------------
Alternative Installation (non-pip)
----------------------------------

Instead of using pip, we can clone the repository locally. This is more useful if you might work on DAX development for instance:

::

	git clone https://github.com/VUIIS/dax.git /local/path/dax
	dax setup
        XnatCheckLogin --host http://129.59.135.143:8080/xnat
        # When prompted, enter user/pwd combination
        # Yes to use as default host
	
