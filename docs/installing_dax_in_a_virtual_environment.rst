Installing DAX in a Virtual Environment
=======================================

Table of Contents
~~~~~~~~~~~~~~~~~

1.  `Setup <#setup>`__
  1.  `OS X Setup <#os-x-setup>`__
2.  `Create the Virtual Environment <#create-the-virtual-environment>`__
3.  `Install DAX <#install-dax>`__
4.  `Verify Installation <#verify-installation>`__


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
	
To setup dax, run the following

::

	(dax) $ dax setup
	########## DAX_SETUP ##########
	Script to setup the ~/.dax_settings.ini files for your dax installation.
	
	Warning: daxnetrc is empty. Setting XNAT login:
	Please enter your XNAT host: <xnat_host_url>
	Please enter your XNAT username: <username>
	Please enter your XNAT password: <password>
	 --> Good login.
	
	Starting to config the dax_settings.ini file:
	  - Section: admin
	    Do you want to set/modify the section [admin] in the settings file? [yes/no] no
	  - Section: cluster
	    Do you want to set/modify the section [cluster] in the settings file? [yes/no] no
	  - Section: dax_manager
	    Do you want to set/modify the section [dax_manager] in the settings file? [yes/no] no
	
	0 error(s) -- dax_setup done.
	########## END ##########

As you can see above, you will be prompted for the XNAT host, the user's XNAT username, and the user's XNAT password. It will also ask whether the admin, cluster, or dax_manager sections of the settings file should be updated. Usually, these settings will not need to be modified and should only really be changed if you're confident of what you're doing.

Next, run XnatCheckLogin, which will verify that the xnat host that was just added through dax setup is usable. XnatCheckLogin can also be used to add new hosts (see below).

::

	(dax) $ XnatCheckLogin
	================================================================
	Checking your settings for XNAT in xnatnetrc file:
	Do you want to see the xnat host saved? [yes/no] yes
	XNAT Hosts stored:
	  - <saved_xnat_host_url>
	Please enter the XNAT host you want to check/add: <new_xnat_host_url>
	Warning: no information stored for host <new_xnat_host_url>.
	Do you want to save XNAT host <new_xnat_host_url> information? [yes/no] yes
	Please enter your XNAT username: <username>
	Please enter your XNAT password: <password>
	Checking XNAT logins for host: <new_xnat_host_url>
	  Connecting to host <new_xnat_host_url> with user <username>...
	   --> Good login.
	Login saved.

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

