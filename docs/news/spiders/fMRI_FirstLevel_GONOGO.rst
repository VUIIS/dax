fMRI_FirstLevel_GONOGO
======================

* **What does it do?**

* **Requirements**

* **Resources** *
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT

* **References**

* **Version History**
<revision> <name> <date> <lines changed>

r2960 | bdb | 2015-07-06 10:34:37 -0500 (Mon, 06 Jul 2015) | 1 line
	Add suffix_proc option for dax 0.3.1, also change vX.X.X to vX_X_X
r2655 | yben | 2015-05-11 09:02:40 -0500 (Mon, 11 May 2015) | 1 line
	Switching Modules/Processors/spiders for the version 0.3.0 of dax package (generic functions build in dax)
r2077 | yben | 2014-12-01 10:16:48 -0600 (Mon, 01 Dec 2014) | 1 line
	fixing new preprocess for firstlevel
r2020 | yben | 2014-11-07 13:26:33 -0600 (Fri, 07 Nov 2014) | 1 line
	Switching fMRI_FirstLevel to use preprocess specific to each sequence.
r1992 | yben | 2014-10-16 12:46:53 -0500 (Thu, 16 Oct 2014) | 2 lines
	Removing MASIMATLAB_PATH called from dax and instead getting path from VUIIS_path_settings.py in processors/
	Adding all the path to processors/VUIIS_path_settings.py for each imaging software used.
r1979 | yben | 2014-10-10 15:07:51 -0500 (Fri, 10 Oct 2014) | 2 lines
	Adding "-singleCompThread" to every matlab called from regular spiders.
	Fixing bedpost problem (using fa.nii instead of dti)
r1903 | yben | 2014-08-15 11:42:56 -0500 (Fri, 15 Aug 2014) | 2 lines
	Final commit to work with the new package dax.
	Fix some imports for modules/spiders/processors/Xnat_tools (fs)
r1901 | yben | 2014-08-15 09:05:31 -0500 (Fri, 15 Aug 2014) | 4 lines
	Important Commit:
	1) Adding new spiders using the new template
	2) Switching old spiders to new template
	3) Using new package dax
r1584 | yben | 2014-03-12 14:31:08 -0500 (Wed, 12 Mar 2014) | 1 line
	set_error if output missing
r1212 | yben | 2013-12-16 15:54:39 -0600 (Mon, 16 Dec 2013) | 1 line
	removing RESMS from the resources since nothing is copied.
r1192 | yben | 2013-12-12 11:00:18 -0600 (Thu, 12 Dec 2013) | 1 line
	Error copying the resources fixed.
r1112 | yben | 2013-12-02 10:30:19 -0600 (Mon, 02 Dec 2013) | 1 line
	debugging first level analysis spider for fMRI
r1105 | yben | 2013-11-22 14:23:29 -0600 (Fri, 22 Nov 2013) | 1 line
	Fixing a resources output name issues.
r1104 | yben | 2013-11-22 14:04:20 -0600 (Fri, 22 Nov 2013) | 1 line
	Fixing a resources output name issues.
r1102 | yben | 2013-11-21 15:26:13 -0600 (Thu, 21 Nov 2013) | 1 line
	Debugging frist level fMRI
r1101 | yben | 2013-11-21 15:18:33 -0600 (Thu, 21 Nov 2013) | 1 line
	Debugging frist level fMRI
r1100 | yben | 2013-11-21 15:04:05 -0600 (Thu, 21 Nov 2013) | 1 line
	Debugging frist level fMRI
r1099 | yben | 2013-11-21 14:53:50 -0600 (Thu, 21 Nov 2013) | 1 line
	Debugging frist level fMRI
r1098 | yben | 2013-11-21 14:47:16 -0600 (Thu, 21 Nov 2013) | 1 line
	Debugging frist level fMRI
r1096 | yben | 2013-11-21 14:36:07 -0600 (Thu, 21 Nov 2013) | 1 line
	Debugging frist level fMRI
r1084 | yben | 2013-11-21 10:25:25 -0600 (Thu, 21 Nov 2013) | 1 line
	Debuggin First level spider
r1056 | yben | 2013-11-15 15:32:28 -0600 (Fri, 15 Nov 2013) | 1 line
	Fixing the fix to go from Spider.py to XnatUtils
r1049 | masispider | 2013-11-15 13:35:55 -0600 (Fri, 15 Nov 2013) | 1 line
	Organizing the folder in a better way with the cci package comming out soon. One folder for the processors, one for the modules and one for the spider working with the new way

**Current Contact Person**
<date> <name> <email / URL> 
