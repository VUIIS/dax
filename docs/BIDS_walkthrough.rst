BIDSMapping: Walkthrough Tutorial
=================================
Introduction
~~~~~~~~~~~~

This is a tutorial for using BIDSMapping tool, a DAX command line tool (https://github.com/VUIIS/dax). The BIDSMapping tool allows the user to create, update or replace rules/mapping at the project level on XNAT. For using BIDSMapping tool you require 

- the lastest verion of DAX installed. Please check https://dax.readthedocs.io/en/latest/installing_dax_in_a_virtual_environment.html to install DAX in a virtual environment.

- A project on XNAT with imaging data. 

- A dcm2niix module turned on for the project. Preferred if the dcm2niix_bids module is turned on for the project. The dcm2niix_bids will add the required json sidecar. However, the BIDSMapping tool is capable of adding the json sidecar when missing.

Table of Contents
~~~~~~~~~~~~~~~~~

1.  `Step 1 Mapping Datatype and Scans <#step-1-mapping-datatypes-and-scans>`__
2.  `Step 2 Upload Datatype Mapping to XNAT <#step-2-upload-datatype-mapping-to-xnat>`__
3.  `Step 3 Check Project Level File Manager <#step-3-check-project-level-file-manager>`__
4.  `Step 4 Mapping Tasktype and Scans <#step-4-mapping-tasktype-and-scans>`__
5.  `Step 5 Upload Tasktype Mapping to XNAT <#step-5-upload-tasktype-mapping-to-XNAT>`__
6.  `Step 6 Mapping Repetition Time and Scans <#step-6-mapping-repetition-time-and-scans>`__
7.  `Step 7 Upload Repetition Time Mapping to XNAT <#step-7-upload-repetition-time-mapping-to-xnat>`__
8.  `Step 8 Check Project Level File Manager <#step-8-check-project-level-file-manager>`__
9.  `Step 9 Mapping Perfusion Imaging Type <#step-9-bids-map-perfusion>`__
10. `Step 10 Upload Perfusion Type to XNAT <#step-10-upload-asl-type>`__
11. `Step 11 Check Project Level File Manager <#step-11-check-project-level-file-manager>`__
12. `Additional Useful BIDSMapping Tool Options <#additional-useful-bidsmapping-tool-options>`__
13. `Step 12 Correct Old Mapping <#step-12-correct-out-mapping>`__
14. `Step 13 Replace Existing Mapping <#step-13-replace-existing-mapping>`__
15. `Step 14 Check Corrected LOGFILE <#step-14-check-corrected-logfile>`__
16. `Step 15 Add New Mapping <#step-15-add-new-mapping>`__
17. `Step 16 Update Existing Mapping <#step-16-update-existing-mapping>`__
18. `Step 17 Check Updated LOGFILE <#step-17-check-updated-logfile>`__


---------------------------------
Step 1 Mapping Datatype and Scans
---------------------------------

You need to create a mapping for BIDS datatype and scans on XNAT. First, create the CSV file of the mapping that you would like to upload to XNAT.

Open a CSV file

::

	(dax) $ vim (or nano or any editor you like) datatype.csv

Type the series_description and datatype you want to map

::

	series_description,datatype
	T1,anat
	gonogo1,func
	gonogo2,func
	cap1,func
	cap2,func
	mid1,func
	mid2,func
	mid3,func


Please note, instead of scan_type in column 1 header series_description can also be used. Make sure the scan_type or series_description is from the scan on XNAT. Image below shows where the information can be found on XNAT

        .. image:: images/BIDS_walkthrough/Step1.1.PNG

Datatype column correspond to the BIDS datatype folder (https://bids.neuroimaging.io/) for the scan to be in. BIDS datatype folder is either 
- anat (structural imaging such as T1,T2,etc.), 
- func (task based and resting state functional MRI), 
- fmap (field inhomogeneity mapping data such as fieldmaps) or 
- dwi (diffusion weighted imaging).
For more information checkout page 4 and 8 in https://www.biorxiv.org/content/biorxiv/suppl/2016/05/12/034561.DC4/034561-1.pdf

--------------------------------------
Step 2 Upload Datatype Mapping to XNAT
--------------------------------------

This step allows the user to upload datatype mapping rules to XNAT. These mapping rules are then later used by XnatToBids function to organise the scan from XNAT in the respective BIDS datatype folder. 
Upload the CSV file (from Step 1) with the mapping rules to XNAT project level using BIDSMapping --create. If scan_type is used as column 1 header in Step 1, use --xnatinfo scan_type option. 

::

	(dax) $ BIDSMapping --project ZALD_TTS --create datatype.csv --type datatype --xnatinfo series_description

::

	################################################################
	#                     BIDSMAPPING                              #
	#                                                              #
	# Developed by the MASI Lab Vanderbilt University, TN, USA.    #
	# If issues, please start a thread here:                       #
	# https://groups.google.com/forum/#!forum/vuiis-cci            #
	# Usage:                                                       #
	#     Upload rules/mapping to Project level on XNAT.           #
	# Parameters:                                                  #
	#     Project ID           -> ZALD_TTS                         #
        #     XNAT mapping type    -> series_description               #
        #     BIDS mapping type    -> datatype                         #
        #     Create mapping with  -> datatype.csv                     #
	################################################################
	
	INFO: connection to xnat <http://129.59.135.143:8080/xnat>:
	The info used from XNAT is series_description
	CSV mapping format is good
	date 16-06-20-20:05:56
	CREATED: New mapping file 06-16-20-20:05:56_datatype.json is uploaded
	

---------------------------------------
Step 3 Check Project Level File Manager
---------------------------------------

Check Manage Files on XNAT project level. There will be two Resources created; one for XNAT type and the other for datatype mapping. XNAT type will have text file with either scan_type or series_description in it. Datatype mapping will have a .json file of the mapping and a LOGFILE.txt with the logging of rules added and deleted.

        .. image:: images/BIDS_walkthrough/Step3.1.PNG

Steps 4 through 8 are ONLY FOR FUNCTIONAL SCANS
---------------------------------
Step 4 Mapping Tasktype and Scans
---------------------------------

For functional scans, tasktype mapping is necessary. These mapping rules are to map the scan in XNAT to the task. The task refers to the task performed by the subject during the MRI acquisition (For example: rest for resting state). The task could be any activity. The task is required for BIDS filenaming. For more information check out page 11 in https://www.biorxiv.org/content/biorxiv/suppl/2016/05/12/034561.DC4/034561-1.pdf

Similar to Step 1, create tasktype CSV mapping.

::

	(dax) $ vim (or nano or any editor you like) tasktype.csv

::

	series_description,tasktype
	gonogo1,gonogo
	gonogo2,gonogo
	cap1,cap1
	cap2,cap2
	mid1,mid1
	mid2,mid2
	mid3,mid3

--------------------------------------
Step 5 Upload Tasktype Mapping to XNAT
--------------------------------------

This step allows the user to upload tasktype mapping rules to XNAT. The XnatToBids in DAX uses this tasktype mapping to name the funcational scans in the BIDS folder. If there is no tasktype mapping the BIDS conversion will fail for functional scans.

Similar to Step 2, upload the Step 4 CSV mapping to XNAT using BIDMapping tool. 

::

	(dax) $ BIDSMapping --project ZALD_TTS --create tasktype.csv --type tasktype --xnatinfo series_description

::

	################################################################
	#                     BIDSMAPPING                              #
	#                                                              #
	# Developed by the MASI Lab Vanderbilt University, TN, USA.    #
	# If issues, please start a thread here:                       #
	# https://groups.google.com/forum/#!forum/vuiis-cci            #
	# Usage:                                                       #
	#     Upload rules/mapping to Project level on XNAT.           #
	# Parameters:                                                  #
	#     Project ID           -> ZALD_TTS                         #
        #     XNAT mapping type    -> series_description               #
        #     BIDS mapping type    -> tasktype                         #
        #     Create mapping with  -> tasktype.csv                     #
	################################################################
	
	INFO: connection to xnat <http://129.59.135.143:8080/xnat>:
	The info used from XNAT is series_description
	CSV mapping format is good
	date 16-06-20-20:12:12
	CREATED: New mapping file 06-16-20-20:12:12_tasktype.json is uploaded

---------------------------------------------
Step 6 Upload Repetition Time Mapping to XNAT
---------------------------------------------

For functional scan, repetition time (TR) CSV mapping is necessary. This is because there could be some error in the TR found in the NIFTI header or in the JSON sidecar. In order to get the correct TR, we require the user to upload TR and XNAT scan mapping. 


::

	(dax) $ vim (or nano or any editor you like) repetition_time.csv

::

	series_description,repetition_time_sec
	gonogo1,0.862
	gonogo2,0.862

---------------------------------------------
Step 7 Upload Repetition Time Mapping to XNAT
---------------------------------------------
 
This step allows the user to upload TR mapping rules to XNAT. TR value is vital during processing. If there is no repetition time mapping the BIDS conversion will fail for functional scans. 

Upload the above Step 6 mapping to XNAT using the BIDSMapping tool

::

	(dax) $ BIDSMapping --project ZALD_TTS --create repetition_time.csv --type repetition_time_sec --xnatinfo series_description

::

	################################################################
	#                     BIDSMAPPING                              #
	#                                                              #
	# Developed by the MASI Lab Vanderbilt University, TN, USA.    #
	# If issues, please start a thread here:                       #
	# https://groups.google.com/forum/#!forum/vuiis-cci            #
	# Usage:                                                       #
	#     Upload rules/mapping to Project level on XNAT.           #
	# Parameters:                                                  #
	#     Project ID           -> ZALD_TTS                         #
        #     XNAT mapping type    -> series_description               #
        #     BIDS mapping type    -> repetition_time_sec              #
        #     Create mapping with  -> repetition_time.csv              #
	################################################################
	
	INFO: connection to xnat <http://129.59.135.143:8080/xnat>:
	The info used from XNAT is series_description
	CSV mapping format is good
	date 16-06-20-20:15:50
	CREATED: New mapping file 06-16-20-20:15:50_repetition_time_sec.json is uploaded

---------------------------------------
Step 8 Check Project Level File Manager 
---------------------------------------

Check Manage Files on XNAT project level. There should be two more BIDS Resources created. One for TR mapping and another for tasktype mapping. 

        .. image:: images/BIDS_walkthrough/Step8.1.PNG

-------------------------------------
Step 9 Mapping Perfusion Imaging Type
-------------------------------------

For perfusion imaging, you need to create a mapping for BIDS perfusion type on XNAT. First, create the CSV file of the mapping that you would like to upload to XNAT.

Open a CSV file

::

	(dax) $ vim (or nano or any editor you like) asltype.csv

Type the series_description and asltype you want to map

::

	series_description,asltype
	ASL,asl
	pCASL,asl
	ASL_m0,m0scan
	pCASL_M0,m0scan


ASLtype column correspond to the required BIDS naming structure for perfusion imaging type (https://bids.neuroimaging.io/). BIDS datatype folder is either 
- asl (Perfusion imaging scan such as ASL,CASL,pCASL,pASL,etc.), 
- m0scan (Reference scan for blood flow calculation. If included in asl image, do not map.), 

For more information check out https://docs.google.com/document/d/15tnn5F10KpgHypaQJNNGiNKsni9035GtDqJzWqkkP6c


-------------------------------------
Step 10 Upload Perfusion Type to XNAT
-------------------------------------

This step allows the user to upload asltype mapping rules to XNAT. If there is no asltype mapping the BIDS conversion will fail for perfusion scans. 

Upload the above Step 9 mapping to XNAT using the BIDSMapping tool

::

	(dax) $ BIDSMapping --project ZALD_TTS --create asltype.csv --type asltype --xnatinfo series_description

::

	################################################################
	#                     BIDSMAPPING                              #
	#                                                              #
	# Developed by the MASI Lab Vanderbilt University, TN, USA.    #
	# If issues, please start a thread here:                       #
	# https://groups.google.com/forum/#!forum/vuiis-cci            #
	# Usage:                                                       #
	#     Upload rules/mapping to Project level on XNAT.           #
	# Parameters:                                                  #
	#     Project ID           -> EmotionBrain                     #
        #     XNAT mapping type    -> series_description               #
        #     BIDS mapping type    -> asltype		               #
        #     Create mapping with  -> asltype.csv                      #
	################################################################
	
	INFO: connection to xnat <http://129.59.135.143:8080/xnat>:
	The info used from XNAT is series_description
	CSV mapping format is good
	date 16-06-20-20:15:50
	CREATED: New mapping file 06-16-20-20:15:50_asltype.json is uploaded

---------------------------------------
Step 11 Check Project Level File Manager 
---------------------------------------

Check Manage Files on XNAT project level. There should be one more BIDS Resource created for asltype mapping.

        .. image:: images/BIDS_walkthrough/Step11.1.PNG


Additional Useful BIDSMapping Tool Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


There are additional options such as --replace and --update

- The user can use --replace option to remove existing rules and add new rules. This is useful when the user made a mistake in creating the rules and the rules need to be deleted and replaced by new ones. Please note, the steps 9-11 can be followed for using the option --replace in the BIDSMapping tool. 

- The user can use --update option to add new mapping rules to the existing mapping at the project level. This is useful when the user added new scans with new scan types to a project and would like to add mapping rules for these scan types. Please note, the steps 12-14 can be followed for using the option --update in the BIDSMapping tool.

--------------------------
Step 12 Correct Old Mapping 
--------------------------

To replace a mapping at project level, create the new CSV mapping. Here, we are replacing repetition_time mapping.

::

	(dax) $ vim (or nano or any editor you like) correct_repetition_time.csv

::

	series_description,repetition_time_sec
	gonogo1,2
	gonogo2,2

--------------------------------
Step 13 Replace Existing Mapping
--------------------------------

Use option --replace in the BIDSMapping tool. --replace removes the old mapping rules and adds new ones.

::

	(dax) $ BIDSMapping --project ZALD_TTS --replace correct_repetition_time.csv --type repetition_time_sec --xnatinfo series_description

::

	################################################################
	#                     BIDSMAPPING                              #
	#                                                              #
	# Developed by the MASI Lab Vanderbilt University, TN, USA.    #
	# If issues, please start a thread here:                       #
	# https://groups.google.com/forum/#!forum/vuiis-cci            #
	# Usage:                                                       #
	#     Upload rules/mapping to Project level on XNAT.           #
	# Parameters:                                                  #
	#     Project ID           -> ZALD_TTS                         #
        #     XNAT mapping type    -> series_description               #
        #     BIDS mapping type    -> repetition_time_sec              #
        #     Create mapping with  -> correct_repetition_time.csv      #
	################################################################
	
	INFO: connection to xnat <http://129.59.135.143:8080/xnat>:
	The info used from XNAT is series_description
	CSV mapping format is good
	UPDATED: uploaded mapping file 06-16-20-20:25:47_repetition_time_sec.json

-------------------------------
Step 14 Check Corrected LOGFILE
-------------------------------

Check the LOGFILE.txt or json mapping at the XNAT project level under the repetition time Resources.

        .. image:: images/BIDS_walkthrough/Step14.1.PNG

-----------------------
Step 15 Add New Mapping 
-----------------------

To update a mapping at project level, create the new CSV mapping. Here, we are updating repetition_time mapping.

::

	(dax) $ vim (or nano or any editor you like) add_new_repetition_time.csv

::

	series_description,repetition_time_sec
	cap1,2
	cap2,2
	mid1,2
	mid2,2
	mid3,2

--------------------------------
Step 16 Update Existing Mapping
--------------------------------

Use option --update in the BIDSMapping tool. --update add the new mapping rules to the existing mapping rules.

::

	(dax) $ BIDSMapping --project ZALD_TTS --update add_new_repetition_time.csv --type repetition_time_sec --xnatinfo series_description

::

	################################################################
	#                     BIDSMAPPING                              #
	#                                                              #
	# Developed by the MASI Lab Vanderbilt University, TN, USA.    #
	# If issues, please start a thread here:                       #
	# https://groups.google.com/forum/#!forum/vuiis-cci            #
	# Usage:                                                       #
	#     Upload rules/mapping to Project level on XNAT.           #
	# Parameters:                                                  #
	#     Project ID           -> ZALD_TTS                         #
        #     XNAT mapping type    -> series_description               #
        #     BIDS mapping type    -> repetition_time_sec              #
        #     Create mapping with  -> add_new_repetition_time.csv      #
	################################################################
	
	INFO: connection to xnat <http://129.59.135.143:8080/xnat>:
	The info used from XNAT is series_description
	CSV mapping format is good
	UPDATED: uploaded mapping file 06-23-20-16:36:36_repetition_time_sec.json

-----------------------------
Step 17 Check Updated LOGFILE
-----------------------------

Check the LOGFILE.txt or json mapping at the XNAT project level under the repetition time Resources.

        .. image:: images/BIDS_walkthrough/Step17.1.PNG
	
	
	
	
