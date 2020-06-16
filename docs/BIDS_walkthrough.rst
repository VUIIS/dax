BIDSMapping: Walkthrough Tutorial
=================================

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
9.  `Additional Useful BIDSMapping Tool Options <#additional-useful-bidsmapping-tool-options>`__
10.  `Step 9 New Mapping <#step-9-new-mapping>`__
11. `Step 10 Replace Existing Mapping <#step-10-replace-existing-mapping>`__
12. `Step 11 Check LOGFILE <#step-11-check-logfile>`__

---------------------------------
Step 1 Mapping Datatype and Scans
---------------------------------

You need to create a mapping for BIDS datatype and scans on XNAT. First, create the CSV file of the mapping that you would like to upload to XNAT.

Open a CSV file

::

	vim (or nano or any editor you like) woodward_datatype.csv

Type the scan_type and datatype you want to map

::

	scan_type,datatype
	T1W/3D/TFE,anat
	Resting State,func

Please note, instead of scan_type in column 1 header series_description can also be used. Make sure the scan_type or series_description is from the scan on XNAT and datatype is either anat, func, fmap or dwi.

--------------------------------------
Step 2 Upload Datatype Mapping to XNAT
--------------------------------------

Then, upload the mapping CSV file to XNAT project level using BIDSMapping tool. If series_description is used as column 1 header in Step 1, use --xnatinfo series_description option.

::

	BIDSMapping --project WOODWARD_TCP --create /Users/kanakap/woodward_datatype.csv --type datatype --xnatinfo scan_type

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
	#     Project ID           -> WOODWARD_TCP                     #
        #     XNAT mapping type    -> scan_type                        #
        #     BIDS mapping type    -> datatype                         #
        #     Create mapping with  -> .../woodward_datatype.csv        #
	################################################################
	
	INFO: connection to xnat <http://129.59.135.143:8080/xnat>:
	The info used from XNAT is scan_type
	CSV mapping format is good
	date 15-06-20-12:00:06
	CREATED: New mapping file 06-15-20-12:00:06_datatype.json is uploaded
	

---------------------------------------
Step 3 Check Project Level File Manager
---------------------------------------

Check Manage Files on XNAT project level. There will be two Resources created. 

        .. image:: images/BIDS_walkthrough/Step3.1.PNG

---------------------------------
Step 4 Mapping Tasktype and Scans
---------------------------------

For functional scans, tasktype and repetition time mapping (Step 6 and 7) is required. Similar to Step 1, create tasktype CSV mapping.

::

	vim (or nano or any editor you like) woodward_tasktype.csv

::

	scan_type,tasktype
	Resting State,rest

--------------------------------------
Step 5 Upload Tasktype Mapping to XNAT
--------------------------------------

Similar to Step 2, upload to above Step 4 mapping to XNAT using BIDMapping tool.

::

	BIDSMapping --project WOODWARD_TCP --create /Users/kanakap/woodward_tasktype.csv --type tasktype --xnatinfo scan_type

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
	#     Project ID           -> WOODWARD_TCP                     #
        #     XNAT mapping type    -> scan_type                        #
        #     BIDS mapping type    -> tasktype                         #
        #     Create mapping with  -> .../woodward_tasktype.csv        #
	################################################################
	
	INFO: connection to xnat <http://129.59.135.143:8080/xnat>:
	The info used from XNAT is scan_type
	CSV mapping format is good
	date 15-06-20-12:22:10
	CREATED: New mapping file 06-15-20-12:22:10_tasktype.json is uploaded

---------------------------------------------
Step 6 Upload Repetition Time Mapping to XNAT
---------------------------------------------

For functional scan, create repetition CSV mapping.


::

	vim (or nano or any editor you like) woodward_repetition_time.csv

::

	scan_type,repetition_time_sec
	Resting State,2

---------------------------------------------
Step 7 Upload Repetition Time Mapping to XNAT
---------------------------------------------

Upload the above Step 6 mapping to XNAT using the BIDSMapping tool.

::

	BIDSMapping --project WOODWARD_TCP --create /Users/kanakap/woodward_repetition_time.csv --type repetition_time_sec
	--xnatinfo scan_type

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
	#     Project ID           -> WOODWARD_TCP                     #
        #     XNAT mapping type    -> scan_type                        #
        #     BIDS mapping type    -> repetition_time_sec              #
        #     Create mapping with  -> .../woodward_repetition_time.csv #
	################################################################
	
	INFO: connection to xnat <http://129.59.135.143:8080/xnat>:
	The info used from XNAT is scan_type
	CSV mapping format is good
	date 15-06-20-12:27:40
	CREATED: New mapping file 06-15-20-12:27:40_tasktype.json is uploaded

---------------------------------------
Step 8 Check Project Level File Manager 
---------------------------------------

Check Manage Files on XNAT project level. There should be four Resources. 

        .. image:: images/BIDS_walkthrough/Step8.1.PNG

Additional Useful BIDSMapping Tool Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Please note, the steps 9-11 can be followed for using the option --update in the BIDSMapping tool. This option allows you to ONLY add new mapping rules to existing mapping at the project level.

------------------
Step 9 New Mapping
------------------

To replace a mapping at project level, create the new CSV mapping. Here, we are replacing repetition_time mapping.

::

	vim (or nano or any editor you like) woodward_repetition_time.csv

::

	scan_type,repetition_time_sec
	Resting State,0.826

--------------------------------
Step 10 Replace Existing Mapping
--------------------------------

Use option --replace in the BIDSMapping tool. --replace removes the old mapping rules and adds new ones.

::

	BIDSMapping --project WOODWARD_TCP --replace /Users/kanakap/woodward_repetition_time.csv --type repetition_time_sec 		--xnatinfo scan_type

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
	#     Project ID           -> WOODWARD_TCP                     #
        #     XNAT mapping type    -> scan_type                        #
        #     BIDS mapping type    -> repetition_time_sec              #
        #     Create mapping with  -> .../woodward_repetition_time.csv #
	################################################################
	
	INFO: connection to xnat <http://129.59.135.143:8080/xnat>:
	The info used from XNAT is scan_type
	CSV mapping format is good
	date 15-06-20-12:35:50
	UPDATED: New mapping file 06-15-20-12:35:50_tasktype.json is uploaded

---------------------
Step 11 Check LOGFILE
---------------------

Check the LOGFILE.txt or json mapping at the XNAT project level under the repetition time Resources.

        .. image:: images/BIDS_walkthrough/Step11.1.PNG
