Upload Data to XNAT
===================

Table of Contents
~~~~~~~~~~~~~~~~~

1.  `Upload Data to XNAT <#upload-data-to-xnat>`__
2.  `Upload DICOM <#upload-dicom>`__
3.  `Upload Using the GUI <#upload-using-the-gui>`__
4.  `Uploading Using XnatUpload <#uploading-using-xnatupload>`__
5.  `Verifying Data is in Upload Queue <#verifying-data-is-in-upload-queue>`__

-------------------
Upload Data to XNAT
-------------------

Uploading data to XNAT can be done several ways:

- Upload DICOM through the XNAT prearchive
- Upload imaging data from the GUI (inefficient for more than one resource to upload)
- Xnatupload (very efficient for large batch of different data)

If you are uploading bulk data, please contact us first. "Bulk" should be considered anything over 10Gb. Uploading can take a long time so we want to ensure that it is done the way that you want first so it doesn't have to be deleted and re-uploaded. Additionally, please do not run multiple parallel uploads at once. Limit this at maximum to two. If you have special considerations, please let us know.

Upload DICOM
~~~~~~~~~~~~

Uploading only DICOM to XNAT can be done using tools such as dcm4chee or DicomBrowser. Follow the tutorial Sending DICOM to Vanderbilt XNAT to learn the process of uploading DICOM through XNAT prearchive.

Upload Using the GUI
~~~~~~~~~~~~~~~~~~~~

Uploading imaging data with the GUI is not recommended if you have a large amount of data to upload. You can add folder / resources to any level of the project on XNAT from the action menu (Manage Files). If you browse to any session on your project, you can see this action menu on the right side:

NEED IMAGE

Manage Files will allow you to create a new scan, add a new resource (folder), and upload files. This will allow you to create a new scan:

NEED IMAGE

From then, you can see the three buttons: Add Folder, Upload Files, Update File Data. The first one allows you to create a new resource (example: NIFTI), the second one allows you to upload files to this folder (example: upload your t1.nii.gz) and the last one will update your session to check the archive on XNAT for new files that are not showing on the GUI.

Here is an example of uploading files to the resource NIFTI for a specific file:

NEED IMAGE

Using the GUI doesn't allow the user to upload a large number of data. We will see in the next paragraph how we can do that with Xnatupload.

Warning: you can not create an assessor from the GUI.

Uploading Using XnatUpload
~~~~~~~~~~~~~~~~~~~~~~~~~~

Xnatupload requires the user to generate a specific CSV to upload data to XNAT. You can find more information and examples on Vanderbilt XNAT Tools We will upload a new subject to our test project to show the process.

- Writing CSV

The CSV for Xnatupload needs a specific header:

- object_type,project_id,subject_label,session_type,session_label,as_label,as_type,as_description,quality,resource,fpath

where:

- object_type is either "scan" or "assessor" to specify to the tool which type of data you want to upload
- project_id,subject_label,session_label corresponds to the label of the different objects
- session_type is the type of session you want to upload (MR/CT/PET...), you can see all of the modality with -printmodality
- as_label corresponds to assessor or scan label
- as_type corresponds to proctype or scantype
- as_description corresponds to procstatus or series description for the scan
- quality corresponds to qastatus or quality for scan
- resource is the name of the folder/resource you want to upload (\*\*E.G: NIFTI or DICOM)
- fpath is the full path to the resource on your computer. It can be a folder in which case it will upload all the resources in the folder or a file.

** Please note that a resource is just folder name and you can use whatever you want. However, all of the code expects any DICOM file to be in a "DICOM" resource, any NIfTI file to be in a "NIFTI" resource, any PAR file to be in a "PAR" resource and any REC file to be in a "REC" resource. Please use these resource names as much as possible. If you have anything that fits out of this scope that you thing should become a "default", please let us know!

You will need to have one row per resource you want to upload. For example, you can upload two files to a resource like this:

::

	scan,VUSTP,VUSTP11,MR,VUSTP11a,301,T1,T1/3D/TW,questionable,NIFTI,/home/upload/t1.nii.gz
	scan,VUSTP,VUSTP11,MR,VUSTP11a,301,T1,T1/3D/TW,questionable,NIFTI,/home/upload/t1_corrected.nii.gz

or one folder with the two files in it:

::

	scan,VUSTP,VUSTP11,MR,VUSTP11a,301,T1,T1/3D/TW,questionable,NIFTI,/home/ upload/T1s/

Here is the csv we will use to upload a T1 NIFTI and a DTI NIFTI and DICOM to a subject/session on VUSTP:

::

	object_type,project_id,subject_label,session_type,session_label,as_label,as_type,as_description,quality,resource,fpath
	scan,VUSTP,VUSTP11,MR,VUSTP11a,301,T1,T1/3D/TW,questionable,NIFTI,/home/ upload/t1.nii.gz
	scan,VUSTP,VUSTP11,MR,VUSTP11a,401,DTI,diffusion weighted image,questionable,DICOM,/home/upload/dti.dcm
	scan,VUSTP,VUSTP11,MR,VUSTP11a,401,DTI,diffusion weighted image,questionable,NIFTI,/home/upload/dti.nii.gz

If the subject or session doesn't exist, the script will create it for you.

- Check Inputs

The tool will not upload data where we are missing information. When reading the CSV file, it will print a list of warning if the script detects errors. For example, the tool will not upload a scan if the session is not set. You can check what will the script upload to XNAT by using the options -report at the end of your command line:

- Xnatupload -c upload_new_data.csv --report

Here is the output of the command for the previous csv file:

::

	################################################################
	#                          XNATUPLOAD                          #
	#                                                              #
	# Developed by the masiLab Vanderbilt University, TN, USA.     #
	# If issues, email benjamin.c.yvernault@vanderbilt.edu         #
	# Usage:                                                       #
	#     Upload data to XNAT following the csv file information   #
	# Parameters :                                                 #
	#     CSV file             -> upload.csv                       #
	#     Report               -> on                               #
	################################################################
	IMPORTANT WARNING FOR ALL USERS ABOUT XNAT:
	   session_label needs to be unique for each session.
	   Two subjects can NOT have the same session_label
	================================================================
	WARNING: row 1 -- does not start with "scan" or "assessor".
	
	----------------------------------
	Report information about uploading :
	Date: 2015-02-20 13:23:53.699241
	================================================================
	List of the data found in the csv that need to be upload :
	-----------------------------------------
	ObjectType | Project     | Subject        | SessType   | Session            | Label                          
	      | Type            | Description     | Quality           | Resource   | file(s)/folder
	--------------------------------------------------------------------------------------------------------------------
	scan           | VUSTP      | VUSTP11    | MR             | VUSTP11a        | 301                            
	      | T1               | T1/3D/TW        | questionable   | NIFTI        | /home/upload/t1.nii.gz
	scan           | VUSTP      | VUSTP11    | MR             | VUSTP11a        | 401                            
	      | DTI              | diffusion we... | questionable    | DICOM     | /home/upload/dti.dcm
	scan           | VUSTP      | VUSTP11    | MR             | VUSTP11a        | 401                            
	      | DTI              | diffusion we... | questionable    | NIFTI        | /home/upload/dti.nii.gz
	
	--------------------------------------------------------------------------------------------------------------------
	
	INFOS on header:
	 #Description = Job status for assessor or series description for scan
	 #Quality     = Job quality control for assessor or quality for scan (usable/unusable/questionable)
	WARNINGS:
	 #If one of the column is empty for Project/Subject/SessType/Session/Label/resource, the resource will not get upload.
	 #By default, quality is set to questionable for scan and  Needs QA for assessor.
	 #By default, Description (job status) for an assessor will be set to COMPLETE.
	 #IMPORTANT: a session label needs to be unique for a project.
	P.S : Please check that the REC or NII image type that you upload are compressed (.rec/.nii), please compress them in .gz like "file.nii.gz".
	===================================================================

As you can see, a warning row 1 is showing us that the first line doesn't have scan or assessor as an object type and will not get uploaded. The first line of the script corresponds to the header and it makes sense that it will not be uploaded. If you see other rows raising a warning, you should verify your csv file.

- Uploading

If the report looks good to you, you can run the command without the option -report and the script will upload all the data to XNAT. The script will upload new data as well as existing data. It will always warn the user if data already exist. You will need to force the upload or delete the resources via the options to be able to upload those data.

Verifying Data is in Upload Queue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The upload queue is different from the ACCRE queue, which is not involved in the upload process. Upload happens from the '/scratch/$USER/Spider_upload_dir'. The Proc ID should be listed here until it is uploaded to XNAT.
