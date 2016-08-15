intra_sess_reg
==============

* **What does it do?**

* **Requirements**

* **Resources** *
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| MATLAB
| Outputs

* **References**

* **Version History**
<revision> <name> <date> <lines changed>

r2960 | bdb | 2015-07-06 10:34:37 -0500 (Mon, 06 Jul 2015) | 1 line
	Add suffix_proc option for dax 0.3.1, also change vX.X.X to vX_X_X
r2869 | parvatp | 2015-06-16 13:33:15 -0500 (Tue, 16 Jun 2015) | 1 line
	adding new version of dtiQA_v3 created by Bennett to fix issues on opening nifti with several b0
r2655 | yben | 2015-05-11 09:02:40 -0500 (Mon, 11 May 2015) | 1 line
	Switching Modules/Processors/spiders for the version 0.3.0 of dax package (generic functions build in dax)
r2563 | yben | 2015-04-13 11:03:59 -0500 (Mon, 13 Apr 2015) | 1 line
	Fixing nonrigid_reg_to_ATLAS
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
r1816 | yben | 2014-06-09 12:40:37 -0500 (Mon, 09 Jun 2014) | 2 lines
	Debugging intra_sess_reg
r1497 | yben | 2014-02-18 14:58:14 -0600 (Tue, 18 Feb 2014) | 1 line
	Last fix for the spider intra sess reg. Naming the file when downloading them.
r1478 | masispider | 2014-02-13 15:38:12 -0600 (Thu, 13 Feb 2014) | 1 line
	fixing bug on the Spider_intra_sess_reg
r1465 | yben | 2014-02-13 12:17:07 -0600 (Thu, 13 Feb 2014) | 1 line
	Debugging ...
r1461 | yben | 2014-02-11 15:04:33 -0600 (Tue, 11 Feb 2014) | 1 line
	Debugging intra sess reg / nonrigid reg to Atlas
r1383 | masispider | 2014-01-29 10:17:15 -0600 (Wed, 29 Jan 2014) | 1 line
	Spider_intra_sess_reg fixed / working on nonrigid spider
r1378 | yben | 2014-01-28 14:19:03 -0600 (Tue, 28 Jan 2014) | 1 line
	debugging intra sess reg
r1376 | yben | 2014-01-28 14:08:44 -0600 (Tue, 28 Jan 2014) | 1 line
	New version of intra_sess_reg.
r1188 | yben | 2013-12-12 09:31:04 -0600 (Thu, 12 Dec 2013) | 1 line
	Moving Spiders to XnatUtils of the package api/cci
r1049 | masispider | 2013-11-15 13:35:55 -0600 (Fri, 15 Nov 2013) | 1 line
	Organizing the folder in a better way with the cci package comming out soon. One folder for the processors, one for the modules and one for the spider working with the new way

**Current Contact Person**
<date> <name> <email / URL> 
