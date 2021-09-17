============================================
FreeSurfer with DAX in Singularity on SLURM
============================================

This tutorial will guide you through how to use DAX to run FreeSurfer 6 recon-all using singularity containers on a SLURM cluster with all data stored on XNAT.

You can use this guide as a template to get started running your own pipelines with XNAT and DAX.

We assume that you have T1-weighted MR images loaded into XNAT(link) in NIFTI format. We also will assume that one of these NIFTI files is named T1.nii.gz and is located in a project named PROJ1 in a subject named SUBJ1 in session SESS1 in scan SCAN1 with resource NIFTI. And the scan type of SCAN1 is T1. So, the hierarchy looks like:
PROJ1/SUBJ1/SESS1/SCAN1/NIFTI/T1.nii.gz (link to example in XNAT central?)

###################### 
Install DAX data types
######################
In order to store the output from DAX pipelines such as FS6_v1, your XNAT must have the DAX data type installed. This data type can be installed by adding the DAX plugin
to your XNAT system. This will also install customizations to the XNAT interface for DAX. These include custom Image Session pages and displays.

Before installing the DAX plugin, save the current state of your XNAT so you can undo the changes. Specifically, make a backup of your XNAT_HOME, postgres db, and tomcat deployment.

When you are ready to install, stop tomcat and copy the plugin to your server. The DAX plugin is a jar file named dax-plugin-genProcData-X.Y.Z.jar and should be copied to the plugin subdirectory of your XNAT_HOME. With the jar file in place, start tomcat. For more on plugins, consult the XNAT documentation at xnat.org.

#######################
Prepare DAX environment
#######################
1. Log onto the system where you want to run DAX. You will need access to XNAT and be able to run slurm commands.

2. Create this directory structure in home or anywhere else with sufficient space
::
DAX/
	Spider_Upload_Dir/
   	containers/
   	processors/
	settings/

3. job_template.txt

4. Pull the FS6 container
This will download to a SIF file that is 2.6 GB, so you may want to check for sufficient space before running the download.
.. code-block:: bash
cd containers
singularity pull shub://bud42/FS6:v1.2.3

Rename the downloaded file to match the name we are expecting later.
.. code-block:: bash
mv FS6v1.2.3.sif FS6_v1.2.3.simg

5. Create a virtual environment for DAX 
(Skip if you already have dax installed)

.. code-block:: bash
python3 -m venv daxvenv
source daxvenv/bin/activate
pip install dax

6. Download the FS6 processor yaml file 
`FS6 processor.yaml <https://raw.githubusercontent.com/ccmvumc/dax_processors/f4f65c744da1c147ea328c587f90eb1e575bd0d1/FS6_v1.2.3_processor.yaml>`_

7. Move the downloaded file to your DAX/processors directory

8. Next create a settings file named settings.yaml with the contents
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
  - name: fs6
    filepath: FS6_v1.2.3_processor.yaml
projects:
  - project: PROJ1
    yamlprocessors: fs6

Now we test the processor on a single MR session. Find or create a session on XNAT with a scan named "T1". This scan should have a resource named NIFTI with a gzipped nifti file. 

We will use dax to build the slurm batch script, run it on the cluster, and upload the results. 


To build the batch, run:
.. code-block:: bash
dax build --session SESS1 settings.yaml

This will create a new assessor on the session and then write a file in your Spider_Upload_Dir in the subdirectory DISKQ/BATCH. The file will be named the same as the assessor that was created. 

You can check over the file to see if all let's correct. You can also try running the script directly from the command line. When you're ready to launch it on the cluster go to the next step.

To launch the batch, run:
.. code-block:: bash
dax launch --session SESS1 settings.yaml

where PROJECT is the label of the project in XNAT that contains the session and
SESSION is the label of the session. This will submit the batch to SLURM.

You can monitor the job using squeue or using stracejob. To use stracejob, you'll need to find the job ID. This can be determined via squeue or by looking in Spider_Upload_Dir in the jobid file.

The next step is to run dax update after the job is complete. You can run dax update anytime and it will update on job status.
It will have to be run at least once after the job fully completes according to SLURM. 

To update, run:
.. code-block:: bash
dax update settings.yaml

After update has been run on the completed job, we will upload the results to xnat.

To upload, run: 
.. code-block:: bash
dax upload --project PROJ1

This will upload jobs to XNAT for the project named PROJ1. 

After successfully testing, we can configure this processor in a production account.

At Vanderbilt, we maintain a private github repository where we store all of the processor yaml files that we are currently running.

To add a new processor to this repo, we create a new branch with the new processor.
Then we submit a pull request (PR) to add the new processor to the running_processors branch.
This repo is configured to required approval by another user. With approval, you can then merge your own pull request.

After the PR is merged, we pull the updates to the production accounts.
.. code-block:: bash
cd /data/mcr/centos7/dax_processors
git pull origin running_processors

If the singularity image is not already in place, you need to put a copy on the production account.
The location on ACCRE is /data/mcr/centos7/singularity

We can copy a singularity SIF image to ACCRE, or pull from singularity hub (no longer supported for new containers), or pull from docker.

The FS6_v1 can also be pulled from docker if shub is not accessible.
.. code-block:: bash
singularity pull docker://bud42/FS6:v1.2.3

Use the above as a template for testing a new processor. You will need to substitute the processor yaml file and singularity container for those you created for your pipeline. (Link to processors page for help creating a processor yaml.)

You may eventually have enough processors/projects to manage that you will want to use dax manager. This will require access to a REDCap system where you an create new projects for operational purposes. (More here link.)

Now we can "turn on" the processor in our project settings REDCap. But first,
we need to make a new instrument in REDCap for the new processor.

ProcessorFS6v1_2021-09-16_2043.zip
General_2021-09-16_2043.zip
BuildStatus_2021-09-16_2043.zip


Add a new instrument for your new processor
###########################################
Open your DAX project settings in REDCap and add an instrument for the processor. The instruments needs two fields, one to specify the processor file and another to optionally provide arguments.

The file name field is labeled "Processor YAML File". The variable name should begin with the processor name and must have the suffix "_file". For example, the FS6 
file variable name is fs6_v1_file.

You should also provide a default for the processor file. This value will be used to pre-populate field whenver the Processor is turned on for a project. To set the default, modify “Action Tags / Field Annotation”  to be @DEFAULT=”processor.yaml”. Using FS6 as an example, the tag would be @DEFAULT=”FS6_v1.2.3_processor.yaml”

The arguments field is labeled "Processor Arguments". The variable name should begin with the processor name and must have the suffix "_args". For example, the FS6 
file variable name is fs6_v1_args.

# Add processor to existing REDCap
If your REDCap has existing processor instruments, a convenient way to add a new procesor is to copy and edit.
1. Click Designer
1. Click Enter Draft Mode (this allows you to make tentative changes to the REDCAp database and then submit your changes)
1. Find the instrument you want to copy and click Choose Action then Copy
1. Set the new instrument name, e.g for FS6 we use FS6_v1
1. Leave the suffix as "_v2" and click copy instrument
1. Reorder the newly created instrument to be alphabetical in the list
1. Click the newly created instrument to open it
1. Click the pencil to edit the field Processor YAML File
1. Remove "_v2" from the Variable Name and rename it to match the new processor
1. In ActionTags/Field Annotations, change the @DEFAULT value to the new processor yaml file name, 
	e.g. Processor FS6_v1 should have @DEFAULT="FS6_v1.2.3_processor.yaml"
1. Click Save to save changes to the field Processor YAML File
1. Click the pencil to edit the field Processor Arguments
1 Remove "_v2" from the Variable Name and rename it to match the new processor, e.g. fs6_v1_file
1. Click Submit Changes for Review (these changes should be automatically accepted)


Enable a Processor on a Project
###############################
1. Go to DAX Project Settings REDcap project
2. Click Record Status Dashboard
3. Click the project
4. Click the processor to turn on
5. Change 'Complete?' field to 'Complete' and 'Save & Exit Form'


(TODO: how to run dcm2niix in DAX. So users can convert DICOM to NIFTI before running FS6)
(TODO: how to check for the DAX datatype on your XNAT)
(TODO: how to use nrg docker-compose to set up a test xnat instance an load a test image for FS6)
(TODO: how to test slurm commands used by DAX)
(TODO: how to make changes to settings files)
(TODO: how to use a scan named something other than T1)
