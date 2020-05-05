DAX Executables
===============

1.  `DAX Packages <#dax-packages>`__
2.  `How Does it Work? <#how-does-it-work>`__
3.  `DAX Settings <#dax-settings>`__
4.  `How to Write a ProjectSettings.py File <#how-to-write-projectsettings-file>`__
5.  `DAX Executables <#dax-executables>`__
6.  `DAX Build <#dax-build>`__
7.  `DAX Update Tasks <#dax-update-tasks>`__
8.  `DAX Launch <#dax-launch>`__
9.  `DAX Upload <#dax-upload>`__
10. `DAX Manager <#dax-manager>`__

------------
DAX Packages
------------

We have been developing a high throughput pipeline processing and quality assurance environment based on Washington University's XNAT platform. This system has been deployed as the primary data archival platform for all VUIIS studies. This pipeline has been implemented in a python package called Distributed Automation for XNAT (DAX). Data processing occurs on the Vanderbilt Advanced Computing Center for Research and Education (ACCRE). DAX has been developed with a series of settings making the package portable on any batch scripting system. Each customized module is a spider that performs an image processing task using a variety of open source software.

DAX is available on github at https://github.com/VUIIS/dax and be installed with "pip install dax".

How Does it Work?
~~~~~~~~~~~~~~~~~

DAX consists of three main executables that communicates with an XNAT system to process and archived imaging data. XNAT has an object implemented as a child of a session that is called an Assessor that corresponds to processed data. By reading the database on a project basis, the different executables will generate the assessors, check for inputs, run the scripts on the cluster as a job, check on the status of the jobs, and upload data back to XNAT. DAX will also maintain data on REDCap. DAX uses a settings files to specify various customizations of the DAX installation and to specify which processes each project should run and any customizations to the processes.

DAX Settings
~~~~~~~~~~~~

Inside the package DAX, there is a dax_settings.py file. This file contains variables that can be set by the user such as the commands used by your cluster, the different paths (the upload directory, root job, etc...), email settings, or REDCap settings for dax_manager.

By default, the package is set to use the settings used by Vanderbilt University. It's set for SLURM cluster.

How to Write a ProjectSettings.py File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two of the DAX executables will need a ProjectSettings.py file to run. This file is a python script providing the description of each modules/processors that need to run for a project or a list of projects. You can learn on how to write a ProjectSettings.py file here: Writing a settings file.

---------------
DAX Executables
---------------

The main executables in the DAX package are:

- dax_build
- dax_update_tasks
- dax_launch
- dax_upload
- dax_manager

See image below to understand the role of each executable:

	.. image:: images/dax_executables/life_cycle_of_dax_task.png

DAX Build
~~~~~~~~~

dax_build will build all the projects in your ProjectSettings.py file. It will check each sessions of your project and run the different modules to generate raw images (e.g: converting dicom to nifti, generating preview, extracting physlog, etc...) and generates the assessors from the processors set in the ProjectSettings.py file.

DAX Update Tasks
~~~~~~~~~~~~~~~~

dax_update_tasks handles assessors for all the projects in your ProjectSettings.py file. It will get the list of all the assessors that are "open", meaning with a status from the list below and update each assessors status.

Open assessors status:

- NEED_TO_RUN
- UPLOADING
- JOB_RUNNING
- READY_TO_COMPLETE
- JOB_FAILED

DAX Launch
~~~~~~~~~~

It will submit jobs to the cluster for each assessors that have the status NEED_TO_RUN.

DAX Upload
~~~~~~~~~~

Each job on the cluster will not upload data directly to XNAT but copies the data to a temporary folder on the computer (configured in DAX_settings.py). dax_upload will read each processed data from this folder and will upload them on XNAT under an assessor that was previously created by dax_build

DAX Manager
~~~~~~~~~~~

dax_manager is a last feature of the package that allows users to manage multiple projects from REDCap (https://redcap.vanderbilt.edu). It will automatically generate a ProjectSettings.py file from the REDCap database and will run dax_build/dax_update_tasks/dax_launch from those files.

On the REDCap project, each record corresponds to a project. Each library is a module or a processor that can be enabled and customized by the user.
