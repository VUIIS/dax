ASL_vDEV0
=========

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
r1838 | masispider | 2014-06-13 09:16:49 -0500 (Fri, 13 Jun 2014) | 1 line
	adding veasl spider SMD 13 June 2014
r1800 | masispider | 2014-06-03 12:16:24 -0500 (Tue, 03 Jun 2014) | 1 line
	Adding missing arg to spider and fixing processor for ASL SMD 3 June 2014
r1797 | masispider | 2014-06-03 11:21:31 -0500 (Tue, 03 Jun 2014) | 1 line
	Function name changes to Spider_ASL_vDEV0.py SMD 3 June 2014
r1793 | masispider | 2014-06-03 10:43:10 -0500 (Tue, 03 Jun 2014) | 1 line
	Fixed conflicting args SMD 3 June 2014
r1791 | masispider | 2014-06-03 10:35:19 -0500 (Tue, 03 Jun 2014) | 1 line
	Updated paths to be globally unique SMD 3 June 2014
r1789 | masispider | 2014-06-03 10:25:29 -0500 (Tue, 03 Jun 2014) | 1 line
	Updataed ASL spider to accept new args from processor - SMD 3 June 2014
r1655 | masispider | 2014-03-27 10:03:35 -0500 (Thu, 27 Mar 2014) | 1 line
	missed a closing bracket in ASL spider
r1654 | masispider | 2014-03-27 09:48:05 -0500 (Thu, 27 Mar 2014) | 1 line
	updated ASL, SWI, and MRA spiders to use dynamic script name to aviod generating duplicate assessors
r1652 | masispider | 2014-03-26 21:41:58 -0500 (Wed, 26 Mar 2014) | 1 line
	updates to Spider_ASL_vDEV0.py - works for VEASL type data - Steve Damon 26 March 2014
r1651 | masispider | 2014-03-26 18:21:03 -0500 (Wed, 26 Mar 2014) | 1 line
	spelling error in Spider_ASL_vDEV0.py
r1650 | masispider | 2014-03-26 17:33:08 -0500 (Wed, 26 Mar 2014) | 1 line
	uncommented to send run with xvfb -run - Steve Damon - 26 March 2014
r1649 | masispider | 2014-03-26 15:23:19 -0500 (Wed, 26 Mar 2014) | 1 line
	multiple improvements and bug fixes to asl spider - Steve Damon 26 March 2014
r1645 | masispider | 2014-03-26 13:25:19 -0500 (Wed, 26 Mar 2014) | 1 line
	added XnatUtils to import Steve Damon 26 March 2014
r1642 | masispider | 2014-03-26 11:52:23 -0500 (Wed, 26 Mar 2014) | 1 line
	Updated ASL spider to allow flag for M0 map Steve Damon 26 March 2014
r1637 | masispider | 2014-03-26 10:43:43 -0500 (Wed, 26 Mar 2014) | 1 line
	Added ASL Spider - Steve Damon 26 March 2014

**Current Contact Person**
<date> <name> <email / URL>

	
	
