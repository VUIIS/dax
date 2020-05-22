Installing DAX in a Virtual Environment
=======================================

Table of Contents
~~~~~~~~~~~~~~~~~

1.  `Requirements <#requirements>`__
2.  `Setup <#setup>`__
  1.  `OS X Setup <#os-x-setup>`__
3.  `Create the Virtual Environment <#create-the-virtual-environment>`__
4.  `Install DAX <#install-dax>`__
5.  `Verify Installation <#verify-installation>`__
6. `Installing Specific Versions of DAX <#installing-specific-versions-of-dax>`__


-----
Setup
-----

OS X Setup
~~~~~~~~~~

To install miniconda3 go to https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html . Then choose 'Regular Installation', 'MacOS', and finally 'MiniConda Installer for MacOS'. Download the Python 3.7 bash file and open the terminal. Run the following where the file was downloaded:

::

	bash Miniconda3-latest-MacOSX-x86_64.sh

Follow the prompts until miniconda is installed. Then close and reopen terminal. To display a list of installed packages:

::

	conda list

------------------------------
Create the Virtual Environment
------------------------------

DAX is to be installed only on virtual environments on Python 3. To create a new environment in Miniconda with Python 3.6:

::

	conda create -n dax python=3.6

which can then be activated or deactivated with:

::

	conda activate dax    # Activation of environment
	conda deactivate      # Deactivation of environment

-----------
Install DAX
-----------

Once the virtual environment with Python 3 is created, dax can be installed by using

::

	(dax) $ pip install dax
	(dax) $ dax setup
	(dax) $ XnatCheckLogin
	         # When prompted, enter user/pwd combination
	         # Yes to use as default host

Note that sudo is NOT required when you are in the virtual environment.

-------------------
Verify Installation
-------------------

::

	(dax) $ XnatCheckLogin --host <xnat_host_url>

This should provide 'Good Login' in the prompt or

::

	(dax) $ python
	>>> import dax

which should import without error.

