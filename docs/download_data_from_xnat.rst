Download Data from XNAT
=======================

1.  `How to Download Data? <#how-to-download-data>`__
2.  `Download Directly on XNAT <#download-directly-on-xnat>`__
3.  `Download Images <#download-images>`__
4.  `Manage Files <#manage-files>`__
5.  `Download Using XnatDownload <#download-using-xnatdownload>`__

--------------------
How to Download Data
--------------------

Downloading data from XNAT can be done from the terminal using Xnatdownload or from the web GUI. Depending on your needs, one will be more efficient than the other.

-------------------------
Download Directly on XNAT
-------------------------

When you log on XNAT and you navigate to your project, you should see an action menu on the right side of your window. It should appear like this:

IMAGE HERE

There are two menu options that can be used to download data:

- Download Images
- Manage Files

Manage Files is more efficient if you want to download a single resource for a specific object and Download images is better when you want to download a large batch of data from your project.

Download Images
~~~~~~~~~~~~~~~

Download images will allow you to download all data for a project (from the project level). This action is available only from a project or a session.

At the Project Level
~~~~~~~~~~~~~~~~~~~~

If you click on download images, it will go on the following window:

IMAGE HERE

You can select each sessions and image data you want to download. You can then specify some parameters for the download and click submit to request the data.

At the Session Level
~~~~~~~~~~~~~~~~~~~~

If you click on download images, it will display the following window:

IMAGE HERE

You can select the type of archive file you want your download to be (zip/tar) and each image data you want to download for the sessions and click Download

Manage Files
~~~~~~~~~~~~

Manage Files allows you to see the resources available at each level. Usually Manage Files is not useful for project/subject levels. Manage Files is only useful from a session page. It displays the resources for the session but also the resource for any scan and assessor on the session. On the image below, you can see the action menu for a session:

IMAGE HERE

If you click on Manage Files, you should see a window like the following one and if you click on any Plus icon, you can see a link to the file (clicking on the link will download the file).

IMAGE HERE

WARNING: the scissors Scissors will delete the resource. DON'T USE IT if you don't want to delete resources.

---------------------------
Download Using XnatDownload
---------------------------

Xnatdownload is part of the DAX package. If you followed the Get started with XNAT and DAX link, you should have already all the tools installed and working. If you haven't done that, please go back to the link and follow the different steps for your OS. You can also find information and examples on Xnatdownload on Vanderbilt XNAT Tools.

If you want to download a large batch of imaging data from XNAT, you should probably use Xnatdownload. Here is the help display by the tool:

::

	################################################################
	#                         XNATDOWNLOAD                         #
	#                                                              #
	# Developed by the masiLab Vanderbilt University, TN, USA.     #
	# If issues, email benjamin.c.yvernault@vanderbilt.edu         #
	# Usage:                                                       #
	#     Download data from XNAT with specific search precised by #
	#     the different options                                    #
	# Parameters :                                                 #
	#     No Arguments given                                       #
	#     See the help bellow or Use "Xnatdownload" -h             #
	################################################################
	Usage: Xnatdownload [options]
	What is the script doing :
	  *Download filtered data from XNAT to your local computer using the different options.
	
	Examples:
	  *Download all resources for all scans/assessors in a project: 
	        Xnatdownload -p PID -d /tmp/downloadPID -s all --rs all -a all --ra all
	  *Download NIFTI for T1,fMRI: 
	        Xnatdownload -p PID -d /tmp/downloadPID -s T1,fMRI --rs NIFTI
	  *Download only the outlogs for fMRIQA assessors that failed: 
	        Xnatdownload -p PID -d /tmp/downloadPID -a fMRIQA --status JOB_FAILED --ra OUTLOG
	  *Download PDF for assessors that Needs QA: 
	        Xnatdownload -p PID -d /tmp/downloadPID -a all --qcstatus="Needs QA" --ra OUTLOG
	  *Download NIFTI for T1 for some sessions : 
	        Xnatdownload -p PID -d /tmp/downloadPID --sess 109309,189308 -s all --rs NIFTI
	  *Download same data than previous line but overwrite the data: 
	        Xnatdownload -p PID -d /tmp/downloadPID --sess 109309,189308 -s all --rs NIFTI --overwrite
	  *Download data described by a csvfile (follow template) : 
	        Xnatdownload -d /tmp/downloadPID -c  upload_sheet.csv

Options:

::

	 -h, --help            show this help message and exit
 	-p LIST_SEPARATED_COMMA, --project=LIST_SEPARATED_COMMA
        	               Project(s) ID on Xnat
	 -d DIRECTORY, --directory=DIRECTORY
	                       Directory where the data will be download
	 -D, --oneDirectory    Data will be downloaded in the same directory. No sub-directory.
	 --subj=LIST_SEPARATED_COMMA
	                       filter scans/assessors by their subject label. Format: a comma separated string (E.G: --subj VUSTP2,VUSTP3).
	 --sess=LIST_SEPARATED_COMMA
	                       filter scans/assessors by their session label. Format: a comma separated string (E.G: --sess VUSTP2b,VUSTP3a)
	 -s LIST_SEPARATED_COMMA, --scantype=LIST_SEPARATED_COMMA
	                       filter scans by their types (required to download scans). Format: a comma separated string (E.G : -s T1,MPRAGE,REST). To download all types, set to 'all'. -a LIST_SEPARATED_COMMA, --assessortype=LIST_SEPARATED_COMMA filter assessors by their types (required to download assessors). Format: a comma separated string (E.G : -a fMRIQA,dtiQA_v2,Multi_Atlas). To download all types, set to 'all'. 
	 --WOS=LIST_SEPARATED_COMMA filter scans by their types and removed the one with the specified types. Format: a comma separated string (E.G : --WOS T1,MPRAGE,REST).
	 --WOP=LIST_SEPARATED_COMMA
	                       filter assessors by their types and removed the one with the specified types. Format: a comma separated string (E.G : --WOP fMRIQA,dtiQA).
	 --quality=LIST_SEPARATED_COMMA
	                       filter scans by their quality. Format: a comma separated string (E.G: --quality usable,questionable,unusable).
	 --status=LIST_SEPARATED_COMMA
	                       filter assessors by their job status. Format: a comma separated string.
	 --qcstatus=LIST_SEPARATED_COMMA
	                       filter assessors by their quality control status. Format: a comma separated string.
	 -c CSVPATH, --csvfile=CSVPATH
	                       CSV file with the following header: object_type,project_id,subject_label,session_label,as_label. object_type must be 'scan' or 'assessor' and as_label the scan ID or assessor label.
	 --rs=LIST_SEPARATED_COMMA
	                       Resources you want to download for scans. E.g : --rs NIFTI,PAR,REC.
	 --ra=LIST_SEPARATED_COMMA
	                       Resources you want to download for assessors. E.g : --ra OUTLOG,PDF,PBS.
	 --selectionS=SELECTED_SCAN
	                       Download from only one selected scan.By default : no selection. E.G : project-x-subject-x-experiment-x-scan
	 --selectionP=SELECTED_ASSESSOR
	                       Download from only one selected processor.By default :  no selection. E.G : assessor_label
	 --overwrite           Overwrite the previous data downloaded with the same command.
	 --update              Update the files from XNAT that have been downloaded with the newest version if there is one (not working yet).
	 -o OUTPUTFILE, --output=OUTPUTFILE
	                       Write the display in a file giving to this options.

You should read the different examples and the definition for each options. You can call the tool directly from a terminal.

For example, you decided to download all the dti resources NIFTI and BVAL/BVEC files with the PDF of the dtiQA_v2 assessors. The command line you will run is the following:

- Xnatdownload -p VUSTP -s dti --rs NIFTI,BVAL,BVEC -a dtiQA_v2 --ra PDF -d /tmp/downloadDTI
