dtiQA_Multi
===========

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
r2954 | bdb | 2015-07-06 10:07:54 -0500 (Mon, 06 Jul 2015) | 1 line
	Add suffix_proc option for dax 0.3.1
r2655 | yben | 2015-05-11 09:02:40 -0500 (Mon, 11 May 2015) | 1 line
	Switching Modules/Processors/spiders for the version 0.3.0 of dax package (generic functions build in dax)
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
r1581 | yben | 2014-03-12 11:31:31 -0500 (Wed, 12 Mar 2014) | 1 line
	error() -> set_error() typo error fixed
r1575 | yben | 2014-03-11 11:46:31 -0500 (Tue, 11 Mar 2014) | 1 line
	Adding some line in spider (python code) to check the output before setting to complete
r1528 | yben | 2014-02-25 11:33:31 -0600 (Tue, 25 Feb 2014) | 3 lines
	Removing hard coded path in Multi dtiqa and adding it in the processor and the spider.
	It doesn't change the process.
	For dtiQA_v2_1, export path in the spider. Default in the matlab for MASIFUSION,ART,MIPAV,DTIQA_ATLAS
r1419 | yben | 2014-02-03 10:30:44 -0600 (Mon, 03 Feb 2014) | 1 line
	Error on the tgz filename. Using the nifti fullpath instead of the basename to create the TGZ.
r1364 | masispider | 2014-01-27 08:26:42 -0600 (Mon, 27 Jan 2014) | 1 line
	fixing dtiqa saving the FA map
r1343 | yben | 2014-01-22 15:57:57 -0600 (Wed, 22 Jan 2014) | 1 line
	Fixing Spider name in the output files in the upload directory (depends on the spider script name).
r1334 | masispider | 2014-01-22 09:10:50 -0600 (Wed, 22 Jan 2014) | 1 line
	debugging spider dtiqa multi
r1333 | yben | 2014-01-21 17:01:55 -0600 (Tue, 21 Jan 2014) | 2 lines
	debugging the multi scans dtiqa spider/procesor
r1332 | masispider | 2014-01-21 16:40:46 -0600 (Tue, 21 Jan 2014) | 1 line
	Fixed the spider dtiQA on Multi scans session
r1331 | yben | 2014-01-21 16:05:48 -0600 (Tue, 21 Jan 2014) | 1 line
	Debugging ...
r1326 | yben | 2014-01-20 11:14:57 -0600 (Mon, 20 Jan 2014) | 1 line
	Debugging ...
r1321 | yben | 2014-01-20 10:29:20 -0600 (Mon, 20 Jan 2014) | 2 lines
	debugging the multi scans dtiqa spider/procesor
r1320 | yben | 2014-01-20 09:44:06 -0600 (Mon, 20 Jan 2014) | 1 line
	adding dtiqa multi in svn repository

**Current Contact Person**
<date> <name> <email / URL> 

	
	
