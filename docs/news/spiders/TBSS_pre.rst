TBSS_pre
========

* **What does it do?**

* **Requirements**

* **Resources**
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| MATLAB -
| DATA

* **References**

* **Version History**
<revision> <name> <date> <lines changed>
r2960 | bdb | 2015-07-06 10:34:37 -0500 (Mon, 06 Jul 2015) | 1 line
	Add suffix_proc option for dax 0.3.1, also change vX.X.X to vX_X_X
r2655 | yben | 2015-05-11 09:02:40 -0500 (Mon, 11 May 2015) | 1 line
	Switching Modules/Processors/spiders for the version 0.3.0 of dax package (generic functions build in dax)
r1979 | yben | 2014-10-10 15:07:51 -0500 (Fri, 10 Oct 2014) | 2 lines
	Adding "-singleCompThread" to every matlab called from regular spiders.
	Fixing bedpost problem (using fa.nii instead of dti)
r1951 | yben | 2014-09-29 11:45:44 -0500 (Mon, 29 Sep 2014) | 1 line
	checking pdf file exists before copying.
r1949 | yben | 2014-09-25 11:08:23 -0500 (Thu, 25 Sep 2014) | 1 line
	TBSS preprocessing spider back to right naming convention
r1903 | yben | 2014-08-15 11:42:56 -0500 (Fri, 15 Aug 2014) | 2 lines
	Final commit to work with the new package dax.
	Fix some imports for modules/spiders/processors/Xnat_tools (fs)
r1901 | yben | 2014-08-15 09:05:31 -0500 (Fri, 15 Aug 2014) | 4 lines
	Important Commit:
	1) Adding new spiders using the new template
	2) Switching old spiders to new template
	3) Using new package dax
r1740 | masispider | 2014-05-13 11:58:18 -0500 (Tue, 13 May 2014) | 2 lines
	Fix pdf
r1733 | bdb | 2014-05-08 15:40:22 -0500 (Thu, 08 May 2014) | 1 line
	Disable ps2pdf so that its converted by upload spider
r1132 | bdb | 2013-12-04 11:51:42 -0600 (Wed, 04 Dec 2013) | 1 line
	Add TBSS preprocessing spider, processor, and matlab files.
r1048 | bdb | 2013-11-15 08:47:58 -0600 (Fri, 15 Nov 2013) | 1 line
	TBSS preprocessing Spider to work with api package

**Current Contact Person**
<date> <name> <email / URL> 

	
	
