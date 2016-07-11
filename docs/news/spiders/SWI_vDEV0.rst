SWI_vDEV0
=========

* **What does it do?**

* **Requirements**

* **Resources**
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
r1841 | masispider | 2014-06-13 13:03:29 -0500 (Fri, 13 Jun 2014) | 1 line
	download by scan type rather than number SMD 13 June 2014
r1654 | masispider | 2014-03-27 09:48:05 -0500 (Thu, 27 Mar 2014) | 1 line
	updated ASL, SWI, and MRA spiders to use dynamic script name to aviod generating duplicate assessors
r1628 | masispider | 2014-03-25 12:56:17 -0500 (Tue, 25 Mar 2014) | 1 line
	minor bug fix in swi spider
r1627 | masispider | 2014-03-25 12:37:23 -0500 (Tue, 25 Mar 2014) | 1 line
	path was spelled incorrectly in Spider_SWI_vDEV0.py Steve Damon 25 March 2014
r1626 | masispider | 2014-03-25 12:19:06 -0500 (Tue, 25 Mar 2014) | 1 line
	Fixed a bug in the SWI Spider - Steve Damon 25 March 2014
r1619 | masispider | 2014-03-24 19:27:16 -0500 (Mon, 24 Mar 2014) | 1 line
	Removed verbose flag in SWI processor and and spider Steve Damon 24 March 2014
r1610 | masispider | 2014-03-22 17:30:20 -0500 (Sat, 22 Mar 2014) | 1 line
	Updated SWI Spider Steve Damon 22 March 2014 5:30p.m.

**Current Contact Person**
<date> <name> <email / URL> 

	
	
