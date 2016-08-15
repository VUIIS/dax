LST_vDEV0
=========

* **What does it do?**

* **Requirements**

* **Resources** *
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| DATA -
| MATLAB -
| STATS -

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
r1903 | yben | 2014-08-15 11:42:56 -0500 (Fri, 15 Aug 2014) | 2 lines
	Final commit to work with the new package dax.
	Fix some imports for modules/spiders/processors/Xnat_tools (fs)
r1901 | yben | 2014-08-15 09:05:31 -0500 (Fri, 15 Aug 2014) | 4 lines
	Important Commit:
	1) Adding new spiders using the new template
	2) Switching old spiders to new template
	3) Using new package dax
r1767 | bdb | 2014-06-02 11:32:09 -0500 (Mon, 02 Jun 2014) | 1 line
	Modify matlab paths to include NIFTI
r1724 | bdb | 2014-05-06 21:24:50 -0500 (Tue, 06 May 2014) | 1 line
	Modify matlab path to be more specific to LST directory
r1722 | bdb | 2014-05-06 14:10:49 -0500 (Tue, 06 May 2014) | 1 line
	Modified LST to include STATS files
r1714 | bdb | 2014-05-02 09:20:27 -0500 (Fri, 02 May 2014) | 1 line
	New spider for Lesion Segmentation Toolbox (LST)

**Current Contact Person**
<date> <name> <email / URL> 

	
	
