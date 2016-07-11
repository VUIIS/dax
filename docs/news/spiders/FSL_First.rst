FSL_First
=========

* **What does it do?**

* **Requirements**

* **Resources** *
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| All_results
| STATS
| NII
| MATLAB

* **References**

* **Version History**
<revision> <name> <date> <lines changed>
r2960 | bdb | 2015-07-06 10:34:37 -0500 (Mon, 06 Jul 2015) | 1 line
	Add suffix_proc option for dax 0.3.1, also change vX.X.X to vX_X_X
r2655 | yben | 2015-05-11 09:02:40 -0500 (Mon, 11 May 2015) | 1 line
	Switching Modules/Processors/spiders for the version 0.3.0 of dax package (generic functions build in dax)
r2491 | bdb | 2015-03-26 09:12:33 -0500 (Thu, 26 Mar 2015) | 1 line
	Call fslreorient2std before running FIRST
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
r1850 | yben | 2014-06-19 15:53:11 -0500 (Thu, 19 Jun 2014) | 1 line
	Changing the name of the folder for the output.
r1849 | yben | 2014-06-19 15:33:50 -0500 (Thu, 19 Jun 2014) | 1 line
	Saving the full output dir for FSL_First
r1177 | yben | 2013-12-10 14:25:44 -0600 (Tue, 10 Dec 2013) | 1 line
	adding FSL spider and processors

**Current Contact Person**
<date> <name> <email / URL> 

	
	
