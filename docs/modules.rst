Modules
=======

Table of Contents
~~~~~~~~~~~~~~~~~

1.  `LDAX Modules <#ldax-modules>`__
2.  `Module_Auto_Archive <#module-auto-archive>`__
3.  `Module_Autoseg_Leg <#module-autoseg-leg>`__
4.  `Module_create_b0_scan <#module-create-b0-scan>`__
5.  `Module_dcm2nii <#module-dcm2nii>`__
6.  `Module_Extract_physlog <#module-extract-physlog>`__
7.  `Module_Preview_Nifti <#module-preview-nifti>`__
8.  `Module_Process_ROIs <#module-process-rois>`__
9.  `Module_Project_Summary <#module-project-summary>`__
10. `Module_Set_fMRI_Connectivity_Variables <#module-set-fmri-connectivity-variables>`__
11. `Module_Set_Scan_Type <#module-set-scan-type>`__
12. `Module_set_voxel_res_and_fov <#module-set-voxel-res-and-fov>`__
13. `Module_Sync_Assessor_QC_To_Scan <#module-sync-assessor-qc-to-scan>`__
14. `Module_Sync_REDCap_All <#module-sync-redcap-all>`__
15. `Module_Sync_REDCap_ID <#module-sync-redcap-id>`__
16. `Module_T1_skull_strip <#module_t1_skull_strip>`__
17. `Module_Unique_Series_Description <#module-unique-series-description>`__
18. `DAX 1 Modules <#dax-1-modules>`__
19. `Module_Auto_Archive for DAX 1 <#module-auto-archive-for-dax-1>`__
20. `Module_dcm2niix_bids <#module-dcm2niix-bids>`__
21. `Module_dcm2niix <#module-dcm2niix>`__
22. `Module_parrec2niix <#module-parrec2niix>`__
23. `Module_redcap_sync_yaml <#module-redcap-sync-yaml>`__

------------
LDAX Modules
------------

Module_Auto_Archive
~~~~~~~~~~~~~~~~~~~

The Auto Archive Module allows you to automatically move scans from the XNAT Prearchive into the Archive based on input from a REDCap database.

The REDCap database can be used to assign a Project ID, Subject ID, and Session ID that are different from those assigned on the scanner. Most sessions acquired on VUIIS scanners are initially assigned to a project using the last name of the PI. The initial Subject/Session numbers are based on an incrementing integer on the scanner. With the Auto Archive module, you can automatically archive scans and as part of the archive process, replace the scanner-assigned values with your preferred project names and IDs.

To use the Auto Archive module, you will need a separate REDCap project where you store a record for each MR session. This can be an existing REDCap database with a record per session or a longitudinal database with an event for each session.

The REDCap database should contain fields that store these specific pieces of data:

::

	 Project (the preferred XNAT Project ID, must already exist in XNAT)
	 Subject (the preferred subject ID)
	 Session (the preferred session ID, should begin with the Subject)
	 Session Date (the date the session was acquired, used for sanity checking, formatted as a REDCap date M-D-Y)
	 VUIIS Session ID (the number assigned by the scanner)

The Auto Archive module can be configured to look in specific field names to find these data.

If you are using a REDCap database in conjunction with dax_manager to configure your DAX projects, you can assign these field names there.

::

	 Project Field (the name of the field containing the project ID)
	 Subject Field (the name of the field containing the subject ID) 
	 Session Field (the name of the field containing the session ID)
	 Session Date Field (the name of the field containing the session date)
	 VUIIS Session ID Field (the name of the field containing the project ID)

The Auto Archive module can be configured to look in specific field names to find these data. If you are using a REDCap database in conjunction with dax_manager to configure your DAX projects, you can assign these field names there.

::

	Project Field (the name of the field containing the project ID)
	 Subject Field (the name of the field containing the subject ID) 
	 Session Field (the name of the field containing the session ID)
	 Session Date Field (the name of the field containing the session date)
	 VUIIS Session ID Field (the name of the field containing the project ID)


In addition to configuring the field names for the session REDCap, you will also need to configure these parameters:

::

	 API KEY (an environment variable containing the key)
	 Prearchive Project (the Project ID the session is assigned in the Prearchive)
	 Archive Project (the preferred Project ID you want to assign)
	 Email address for errors (an email address to send any errors that occur while the module is running)
	 Project Map (only used 

You can also optionally configure the Auto Archive module to use a longitudinal database by setting these parameters:

::

	 Subject Event Name (the name of the REDCap event containing the Subject Field)
	 Session Event Name (the name of the REDCap event containing the Fields for Session, Session Date, Project, and VUIIS Session ID)

Note that the same REDCap project can be used for multiple XNAT projects. If you are using a REDCap database with dax_manager you will need to configure the Auto Archive Module for each XNAT project.

Contact
~~~~~~~

Brian D. Boyd

Module_Autoseg_Leg
~~~~~~~~~~~~~~~~~~

This is a half module, half spider. It generates an assessor and the entire process takes less than a minute to run 

Module_create_b0_scan
~~~~~~~~~~~~~~~~~~~~~

Module to create a b0 scan on XNAT - used to create dummy b0 for backwards compatibility with dtiQA_v5 and greater

Module_dcm2nii
~~~~~~~~~~~~~~

Module to generate NIFTI from DICOM with dcm2nii

Module_Extract_physlog
~~~~~~~~~~~~~~~~~~~~~~

Module to extract physlog from secondary files from Scanner 

Module_Preview_Nifti
~~~~~~~~~~~~~~~~~~~~

Module to generate the Preview for a scan from a resource (hosting NIFTI file)

Module_Process_ROIs
~~~~~~~~~~~~~~~~~~~

Module to strip the skull from a structural scan on XNAT

Module_Project_Summary
~~~~~~~~~~~~~~~~~~~~~~

What processes this project is running (also show any custom settings)? What's new this week? Sums of QA results: what needs to be done? What data can be analyzed? What's running now? Are there outliers? What's my average wml, fmri motion, hippocampus, etc? What's in the prearchive? Count unique sessions for each scqa type in REDCap? Sessions from past week. Also, list anything currently stuck at JOB_FAILED. Each processor could display a description of itself and also show the average walltime and memory it's using and how that compares to the requested walltime and memory. Each processor should display the bar chart of passed, failed, needed qa and then display boxplots of each output (or should we pick and choose which to display). Show what modules are enabled for this project.

Module_Set_fMRI_Connectivity_Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'The fmri connectivity spider requires two custom variables to be set at the scan level for each fmri scan. The variables are slorder and dropvols. While easy to set for studies that are no longer collecting data (see: https://github.com/VUIIS/VUIIS_DAX_SUPPORT/blob/master/ABIDE/set_fmriconn2_attributes.py). This module accepts a json object to map sequence variant to the required variable key value pairs.

Module_Set_Scan_Type
~~~~~~~~~~~~~~~~~~~~

Module to set the scan type from a text file

Module_set_voxel_res_and_fov
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Module to generate NIFTI from phillips DICOM. Intermediate step: PARREC format.

Module_Sync_Assessor_QC_To_Scan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Module to set the scan type from a text file

Module_Sync_REDCap_All
~~~~~~~~~~~~~~~~~~~~~~

Module to sync metrics from XNAT to REDCap

Module_Sync_REDCap_ID
~~~~~~~~~~~~~~~~~~~~~

Module to sync metrics from XNAT to REDCap with the ID

Module_T1_skull_strip
~~~~~~~~~~~~~~~~~~~~~

Module to strip the skull from a structural scan on XNAT 

Module_Unique_Series_Description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Module to set the series description to a unique value

-------------
DAX 1 Modules
-------------

Module_Auto_Archive for DAX 1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Module to automatically archive sessions on XNAT following REDCap data

Module_dcm2niix_bids
~~~~~~~~~~~~~~~~~~~~

Module to generate NIFTI + JSON from DICOM with dcm2niix

Module_dcm2niix
~~~~~~~~~~~~~~~

Module to generate NIFTI from DICOM with dcm2niix

Module_parrec2niix
~~~~~~~~~~~~~~~~~~

Module to generate NIFTI from parrec with dcm2niix

Module_redcap_sync_yaml
~~~~~~~~~~~~~~~~~~~~~~~

Module to sync to REDCap
