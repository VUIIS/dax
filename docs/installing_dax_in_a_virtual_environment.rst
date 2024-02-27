Installing DAX in a Virtual Environment
=======================================

Table of Contents
~~~~~~~~~~~~~~~~~

  1.  `Setup <#setup>`__
  2.  `Create the Virtual Environment <#create-the-virtual-environment>`__
  3.  `Install DAX <#install-dax>`__
  4.  `Verify Installation <#verify-installation>`__

-----
Setup
-----

To install miniconda3 go to https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html . Follow the procedure described on the miniconda site to install for your OS. It is very important that you follow the directions closely and not forget to source conda. The main idea is to download the Python 3.7 or newer bash file and open the terminal (using 3.8 and MacOS as an example here). Run the following where the file was downloaded:

::

	bash Miniconda3-latest-MacOSX-x86_64.sh

Follow the prompts until miniconda is installed. Now, source conda and add the path to .bash_profile. Then close and reopen terminal. To display a list of installed packages:

::

	conda list

------------------------------
Create the Virtual Environment
------------------------------

DAX is to be installed only on virtual environments on Python 3. To create a new environment in Miniconda with Python 3.8:

::

	conda create -n daxvenv python=3.8

which can then be activated or deactivated with:

::

	conda activate daxvenv    # Activation of environment
	conda deactivate          # Deactivation of environment

After activating the new environment, git version 2.11+ should be installed. 

 - For ACCRE users, refer to the instructions here: https://dax.readthedocs.io/en/latest/requirements_for_dax_on_accre.html
 - Otherwise, install git using these instructions: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

-----------
Install DAX
-----------

Once the virtual environment with Python 3 is created and the correct version of git is installed, you'll need to install dax itself

::

	(daxvenv) $ pip install dax


Configure an environment variable named XNAT_HOST set to the full url of your xnat server. This can 
be incuded in your startup file (such as .bashrc or .bash_profile).

::

	(daxvenv) $ export XNAT_HOST=https://central.xnat.org

Configure your credentials in a file named ".netrc" in your home directory.

::

	machine <SERVER>
	login <USER>
	password <PASSWORD>

Here SERVER is the server name only. For example, central.xnat.org, not https://xnat.website.com/xnat.
Make sure that the xnat_host is formatted similarly to 'xnat.website.com' NOT 'https://xnat.website.com/xnat'
The full url WILL NOT WORK properly.

File permissions on the .netrc must be user-only, e.g. need to run

::

	chmod go-rwx ~/.netrc

-------------------
Verify Installation
-------------------

Next, run XnatCheckLogin, which will verify that you can log on successfully.

::

	(daxvenv) $ XnatCheckLogin
	================================================================
	Checking your settings for XNAT
	No host specified, using XNAT_HOST environment variable.
	Checking login for host=https://central.xnat.org
	Checking connection:host=https://central.xnat.org, user=someusername
	--> Good login.
	================================================================
