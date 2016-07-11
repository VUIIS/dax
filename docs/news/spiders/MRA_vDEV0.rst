MRA_vDEV0
=========

* **What does it do?**

* **Requirements**

* **Resources** *
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| MATLAB -

* **References**

* **Version History**
<revision> <name> <date> <lines changed>

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
r1654 | masispider | 2014-03-27 09:48:05 -0500 (Thu, 27 Mar 2014) | 1 line
	updated ASL, SWI, and MRA spiders to use dynamic script name to aviod generating duplicate assessors
r1636 | masispider | 2014-03-25 23:07:44 -0500 (Tue, 25 Mar 2014) | 1 line
	fixed spider name so it would upload to the correct assessor in XNAT - Steve Damon 25 March 2014
r1631 | masispider | 2014-03-25 19:04:43 -0500 (Tue, 25 Mar 2014) | 1 line
	Added MRA Spider - Steve Damon 25 March 2014

**Current Contact Person**
<date> <name> <email / URL> 

	
	
