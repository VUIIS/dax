DAX 1.0 & LDAX Standard Operating Procedure in ACCRE Production Accounts
=======================================================================

Table of Contents
~~~~~~~~~~~~~~~~~

1.  `DAX 1.0 <#dax-1.0>`__
2.  `LDAX (Legacy DAX) <#ldax-legacy-dax>`__
3.  `DAX 1.0 Installation on Production Accounts <#dax-1.0-installation-on-production-accounts`__
4.  `DAX 1.0 Source Scripts <#dax-1.0-source-scripts>`__
5.  `DAX 1.0 Pipelines and Repositories <#dax-1.0-pipelines-and-repositories>`__
6.  `DAX 1.0 Semaphores and Logs <#dax-1.0-semaphores-and-logs>`__
7.  `LDAX Installation on Production Accounts <#ldax-installation-on-production-accounts>`__
8.  `LDAX Source Scripts <#ldax-source-scripts>`__
9.  `LDAX Pipelines <#ldax-pipelines>`__

-------
DAX 1.0
-------

Deployed in vuiis_archive_singularity and vuiis_daily_singularity for backend processing on Xnat3 (http://129.59.135.143:8080/xnat). Also recommended for users who utilize the dax tools.

-----------------
LDAX (Legacy DAX)
-----------------

Deployed in vuiisccidev and masispiderdev for backend processing on Xnat2 (xnat2.Vanderbilt.edu:8080/xnat). To be retired when all legacy pipelines are replaced.

-------------------------------------------
DAX 1.0 Installation on Production Accounts
-------------------------------------------

In production accounts, dax1.0 is to be installed only on virtual environments(anaconda, virtualenv, etc) on Python-3.6. Current DAX1.0 virtual environment is in

::

	/data/mcr/centos7/venv/dax-1.0

For installing DAX in a virtual environment, see the Installing DAX in a Virtual Environment page.

----------------------
DAX 1.0 Source Scripts
----------------------

~/.bashrc
~~~~~~~~~

::

	if [ -f /etc/bashrc ]; then
        	. /etc/bashrc
	fi
	source /data/mcr/centos7/bashrc/bashrc-dax1.0.sh
	export XNAT_USER=vuiiscci
	export XNAT_HOST=http://129.59.135.143:8080/xnat
	export XNAT_PASS=**********
	export API_KEY_MASTER_SWITCH=************
	# User specific aliases and functions
	alias ff_squeue='squeue --user $USER -o "%.18i %.9P %.100j %.8u %.2t %.10M %.6D %R"'

bashrc-dax1.0.sh
~~~~~~~~~~~~~~~~

::

	umask 0007
	source /data/mcr/centos7/dax_setup/dax_setup-dax1.0.sh

dax_setup-dax1.0.sh
~~~~~~~~~~~~~~~~~~~

::

	ml Intel Python/3.6.3
	source /data/mcr/centos7/venv/dax-1.0/bin/activate

~/.dax_settings.ini
~~~~~~~~~~~~~~~~~~~

Can be set up using the dax tool "dax setup". Contents of current ~/.dax_settings.ini in SOP

~/.daxnetrc
~~~~~~~~~~~

::

	machine http://129.59.135.143:8080/xnat
	Login
	Password

----------------------------------
DAX 1.0 Pipelines and Repositories
----------------------------------

Yaml processors
~~~~~~~~~~~~~~~

::
	/data/mcr/centos7/dax_processors

https://github.com/VUIIS/yaml_processors.git

YAML project settings
~~~~~~~~~~~~~~~~~~~~~

::
	
	/data/mcr/centos7/dax_project_settings

https://github.com/VUIIS/yaml_project_settings.git

YAML dax modules
~~~~~~~~~~~~~~~~

::
	/data/mcr/centos7/dax_modules

https://github.com/VUIIS/dax_modules.git

Singularity containers
~~~~~~~~~~~~~~~~~~~~~~

::

	/data/mcr/centos7/singularity

Xnat Switch(USED both in DAX1.0 and LDAX)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

	/data/mcr/xnat_kill_switch/

https://github.com/MASILab/xnat_kill_switch.git

---------------------------
DAX 1.0 Semaphores and Logs
---------------------------

Flock Semaphores
~~~~~~~~~~~~~~~~

::

	/data/mcr/centos7/dax_locks

FlagFiles managed by dax
~~~~~~~~~~~~~~~~~~~~~~~~

::
	/scratch/$USER/Spider_Upload_Dir/FlagFiles

LOGS from DAX processes
~~~~~~~~~~~~~~~~~~~~~~~

::

	/data/mcr/centos7/dax_logs

----------------------------------------
LDAX Installation on Production Accounts
----------------------------------------

LDAX is to be installed on a virtual environment with Python2.7. Current environment is in 

::

	/data/mcr/anaconda/dax/ldax_v2

LDAX can be installed with pip once the virtual environment with python2.7 is ready using

::
	
	pip install git+https://github.com/VUIIS/LDax.git

LDAX pip requirements have been added to the SOP document.

-------------------
LDAX Source Scripts
-------------------

~/.bashrc
~~~~~~~~~

Ways to recreate to be discussed.

/data/mcr/dax_setup/ldax_v2_setup.sh
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

	ml Anaconda2/4.4.0
	source activate /data/mcr/anaconda/dax/ldax_v2
	export PATH=/data/mcr/masimatlab/trunk/xnatspiders/python/justinlib_v1_1_0/
	      pythonlib/:/data/mcr/masimatlab/trunk/xnatspiders/python/justinlib_v1_1_0/
	      xnatlib/:$PATH
	ml MATLAB/2017a

~/.dax_settings.ini
~~~~~~~~~~~~~~~~~~~

Can be set up using the dax tool "dax setup". Contents of current ~/.dax_settings.ini in SOP

~/.daxnetrc
~~~~~~~~~~~

::

	machine http://xnat2.vanderbilt.edu:8080/xnat
	login masispider
	password *************

--------------
LDAX Pipelines
--------------

The pipelines of LDAX are all contained in the megadocker. All jobs submitted to the cluster use the megadocker and the pipeline runs independent of the environments of the host launching the singularity container. All dax processes run on the host system and do not use the megadocker. The slurm scripts for the pipelines are generated by the processors.

::

	/data/mcr/masimatlab/trunk/xnatspiders/processors

The modules are launched locally by ldax build.

::

	/data/mcr/masimatlab/trunk/xnatspiders/modules

All /data/mcr/masimatlab is part of a SVN repository

::

	https://www.nitrc.org/svn/masimatlab
