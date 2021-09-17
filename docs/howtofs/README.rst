============================================
FreeSurfer with DAX in Singularity on SLURM
============================================

This tutorial will guide you through how to use DAX to run FreeSurfer 6 recon-all using singularity containers on a SLURM cluster with all data stored on XNAT.

You can use this guide as a template to get started running your own pipelines with XNAT and DAX.

We assume that you have T1-weighted MR images loaded into XNAT in NIFTI format. We also will assume that one of these NIFTI files is named T1.nii.gz and is located in a project named PROJ1 in a subject named SUBJ1 in session SESS1 in scan SCAN1 with resource NIFTI. And the scan type of SCAN1 is T1. So, the hierarchy looks like: PROJ1/SUBJ1/SESS1/SCAN1/NIFTI/T1.nii.gz

###################### 
Install DAX data types
######################
In order to store the output from DAX pipelines such as FS6_v1, your XNAT must have the DAX data type installed. This data type can be installed by adding the DAX plugin
to your XNAT system. This will also install customizations to the XNAT interface for DAX. These include custom Image Session pages and displays.

Before installing the DAX plugin, save the current state of your XNAT so you can undo the changes. Specifically, make a backup of your XNAT_HOME, postgres db, and tomcat deployment.

Download the current plugin version `dax-plugin-genProcData-1.4.2.jar <https://github.com/VUIIS/dax/blob/b616dcb7afa2c895de7f03f7b0a8bff7cd0b2b42/misc/xnat-plugins/dax-plugin-genProcData-1.4.2.jar>`_

When you are ready to install, stop tomcat and copy the plugin to your server. The jar file should be copied to the plugin subdirectory of your XNAT_HOME. With the jar file in place, start tomcat. When XNAT comes back online, it will load plugin contents on top of the base XNAT intallation. For more on plugins, consult the XNAT documentation at xnat.org.

#######################
Prepare DAX environment
#######################

1. Log onto the system where you want to run DAX. You will need to be able to access XNAT via the REST api and be able to run slurm commands.

2. Create this directory structure in home or anywhere else with sufficient space

.. code-block:: bash

   DAX/
     Spider_Upload_Dir/
     containers/
     processors/
     settings/
     templates/

3. Copy job_template.txt to the templates subdirectory `job_template.txt <https://raw.githubusercontent.com/VUIIS/dax_templates/2a3d492904d87ab7e4f012b883661d8d72591ecd/job_template.txt>`_

4. Pull the FS6 container. This will download to a SIF file that is 2.6 GB, so you may want to check for sufficient space before running the download.

.. code-block:: bash

   cd containers
   singularity pull shub://bud42/FS6:v1.2.3

5. Rename the downloaded file to match the name we are expecting later.

.. code-block:: bash

   mv FS6_v1.2.3.sif FS6_v1.2.3.simg

6. Create a virtual environment for DAX (skip if you have already installed dax)

.. code-block:: bash

   cd ../
   python3 -m venv daxvenv
   source daxvenv/bin/activate
   pip install dax

7. Download the FS6 processor yaml file `FS6 processor.yaml <https://raw.githubusercontent.com/ccmvumc/dax_processors/f4f65c744da1c147ea328c587f90eb1e575bd0d1/FS6_v1.2.3_processor.yaml>`_

8. Copy the downloaded file to your DAX/processors directory

9. In your settings subdirectory, create a settings file named settings.yaml with the contents

.. code-block:: yaml

   ---
   processorlib: DAX/processors
   singularity_imagedir: DAX/containers
   resdir: DAX/Spider_Upload_Dir
   jobtemplate: DAX/job_template.txt
   admin_email: YOUR_EMAIL_ADDRESS
   attrs:
     queue_limit: 1
     job_email_options: FAIL
     job_rungroup: YOUR_SLURM_GROUP
     xnat_host: YOUR_XNAT_HOST
   yamlprocessors:
     - name: FS6
       filepath: FS6_v1.2.3_processor.yaml
   projects:
     - project: PROJ1
       yamlprocessors: FS6

#####################################
Run the processor on a single session
#####################################
Now we test the processor on a single MR session. We will run on PROJ1/SUBJ1/SESS1/SCAN1 as described above. We will use dax to build the slurm batch script, run it on the cluster, and upload the results. 


1. Build the batch file

.. code-block:: bash

   dax build --session SESS1 settings.yaml

This will create a new assessor on the session and then write a file in your Spider_Upload_Dir in the subdirectory DISKQ/BATCH. The file will be named the same as the assessor that was created. 

You can check over the file to see if all let's correct. You can also try running the script directly from the command line. When you're ready to launch it on the cluster go to the next step.

2. Launch the batch file

.. code-block:: bash

   dax launch --project PROJ1 --session SESS1 settings.yaml

where PROJ1 is the label of the project in XNAT that contains the session and
SESS1 is the label of the session. This will submit the batch to SLURM.

You can monitor the job using squeue or using stracejob. To use stracejob, you'll need to find the job ID. This can be determined via squeue or by looking in Spider_Upload_Dir in the jobid file for this job.

The next step is to run dax update after the job is complete. You can run dax update anytime and it will update on job status.
It will have to be run at least once after the job fully completes according to SLURM. 

3. Complete the batch

.. code-block:: bash

   dax update --project PROJ1 settings.yaml

After update has been run on the completed job, we will upload the results to xnat.

4. Upload the results

.. code-block:: bash

   dax upload --project PROJ1

This will upload jobs to XNAT for the project named PROJ1. 

Use the above as a template for testing a new processor. You will need to substitute the processor yaml file and singularity container for those you created for your pipeline. Consult the processors docs for help creating a processor yaml.

You may eventually have enough processors/projects to manage that you will want to use dax manager. This will require access to a REDCap system where you an create new projects for operational purposes.

################################
Configure REDCap for DAX manager
################################
To Be Done: use these zip files to create redcap instances for DAX.

ProcessorFS6v1_2021-09-16_2043.zip

General_2021-09-16_2043.zip

BuildStatus_2021-09-16_2043.zip

######################################
Configure the processor for production
######################################

After successfully testing, we can configure this processor to be used in a production account.

At Vanderbilt, we maintain a private github repository where we store all of the processor yaml files that we are currently running.

To add a new processor to this repo, we create a new branch with the new processor.
Then we submit a pull request (PR) to add the new processor to the running_processors branch.
This repo is configured to required approval by another user. With approval, you can then merge your own pull request.

After the PR is merged, we pull the updates to the production accounts.

.. code-block:: bash

  cd /data/mcr/centos7/dax_processors
  git pull origin running_processors

If the singularity image is not already in place, you need to put a copy on the production account. At Vanderbilt, the location on ACCRE is /data/mcr/centos7/singularity

We can copy a singularity SIF image to ACCRE, or pull from singularity hub (no longer supported for new containers), or pull from docker.

The FS6_v1 can also be pulled from docker if shub is not accessible.

.. code-block:: bash

  singularity pull docker://bud42/FS6:v1.2.3

Now we can "turn on" the processor in our project settings REDCap. But first, we need to make a new instrument in REDCap for the new processor.

Add a new instrument for your new processor
###########################################
In your DAX project settings REDCap, add an instrument for the processor. The instrument needs two fields, one to specify the processor file and another to optionally provide arguments.

The file name field is labeled "Processor YAML File". The variable name should begin with the processor name and must have the suffix "_file". For example, the FS6 
file variable name is fs6_v1_file.

You should also provide a default for the processor file. This value will be used to pre-populate field whenver the Processor is turned on for a project. To set the default, modify “Action Tags / Field Annotation”  to be @DEFAULT=”processor.yaml”. Using FS6 as an example, the tag would be @DEFAULT=”FS6_v1.2.3_processor.yaml”

The arguments field is labeled "Processor Arguments". The variable name should begin with the processor name and must have the suffix "_args". For example, the FS6 
file variable name is fs6_v1_args.

Add processor to existing REDCap
------------------------------------

If your REDCap has existing processor instruments, a convenient way to add a new processor is to copy and edit.

#. Click Designer
#. Click Enter Draft Mode (this allows you to make tentative changes to the REDCAp database and then submit your changes)
#. Find the instrument you want to copy and click Choose Action then Copy
#. Set the new instrument name, e.g for FS6 we use FS6_v1
#. Leave the suffix as "_v2" and click copy instrument
#. Reorder the newly created instrument to be alphabetical in the list
#. Click the newly created instrument to open it
#. Click the pencil to edit the field *Processor YAML File*
#. Remove "_v2" from the Variable Name and rename it to match the new processor
#. In ActionTags/Field Annotations, change the @DEFAULT value to the new processor yaml file name, e.g. Processor FS6_v1 should have @DEFAULT="FS6_v1.2.3_processor.yaml"
#. Click Save to save changes to the field *Processor YAML File*
#. Click the pencil to edit the field *Processor Arguments*
#. Remove "_v2" from the Variable Name and rename it to match the new processor, e.g. fs6_v1_args
#. Click Save to save changes to the field *Processor Arguments*
#. Click Submit Changes for Review (these changes should be automatically accepted)


###############################
Enable a Processor on a Project
###############################
#. Go to DAX Project Settings in REDcap
#. Click Record Status Dashboard
#. Click the project you want to modify
#. Click the processor you want to turn on
#. Change 'Complete?' field to 'Complete' (we use Complete to indicate ON, any other values indicates OFF)
#. Click Save & Exit Form

###
TBD
###

- how to run dcm2niix in DAX, to allow users to convert DICOM to NIFTI before running FS6
- how to check for the DAX datatype on your XNAT
- how to use nrg docker-compose to set up a test xnat instance an load a test image for FS6
- how to test slurm commands used by DAX
- how to make changes to settings files
- how to use a scan named something other than T1
