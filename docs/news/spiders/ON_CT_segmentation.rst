ON_CT_segmentation
==================

* **What does it do?**

* **Requirements**

* **Resources** *
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| result -
| MATLAB -

* **References**

* **Version History**
<revision> <name> <date> <lines changed>

r2960 | bdb | 2015-07-06 10:34:37 -0500 (Mon, 06 Jul 2015) | 1 line
	Add suffix_proc option for dax 0.3.1, also change vX.X.X to vX_X_X
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
r1826 | yben | 2014-06-10 16:50:57 -0500 (Tue, 10 Jun 2014) | 1 line
	adding atlas_image to be download for CT ON when it's the atlas
r1824 | yben | 2014-06-10 11:39:24 -0500 (Tue, 10 Jun 2014) | 1 line
	Switching print to sys.stdout.write to see outlog from spider and matlab in the right order
r1822 | yben | 2014-06-10 10:23:36 -0500 (Tue, 10 Jun 2014) | 1 line
	Adding ext matlab path to the pdf maker
r1815 | yben | 2014-06-09 09:48:35 -0500 (Mon, 09 Jun 2014) | 1 line
	fixing the pdf report to use nii.gz
r1315 | yben | 2014-01-17 14:22:00 -0600 (Fri, 17 Jan 2014) | 1 line
	Debugging ...
r1302 | yben | 2014-01-16 10:08:04 -0600 (Thu, 16 Jan 2014) | 1 line
	Debugging ...
r1298 | yben | 2014-01-15 08:37:22 -0600 (Wed, 15 Jan 2014) | 1 line
	Debugging ON segmentation
r1288 | yben | 2014-01-14 10:01:42 -0600 (Tue, 14 Jan 2014) | 1 line
	Fixing ON_segmentaiton with PDF.
r1286 | yben | 2014-01-13 11:57:08 -0600 (Mon, 13 Jan 2014) | 1 line
	debugging ON segmentation with PDF creation.
r1266 | yben | 2014-01-09 11:41:05 -0600 (Thu, 09 Jan 2014) | 1 line
	debugging ON_segmentation
r1252 | yben | 2014-01-08 11:16:13 -0600 (Wed, 08 Jan 2014) | 1 line
	Fixing ON segmentation
r1245 | yben | 2014-01-07 10:21:31 -0600 (Tue, 07 Jan 2014) | 2 lines
	Debugging the ON segmentation spiders
r1241 | yben | 2014-01-06 11:49:25 -0600 (Mon, 06 Jan 2014) | 1 line
	Adding PDF to the ON segmentation spiders.
r1229 | yben | 2013-12-17 16:06:00 -0600 (Tue, 17 Dec 2013) | 1 line
	debugging ON segmentation with PDF
r1222 | yben | 2013-12-17 10:30:43 -0600 (Tue, 17 Dec 2013) | 1 line
	Adding PDF to Spider ON segmentation. Need to try it
r1220 | yben | 2013-12-17 10:26:53 -0600 (Tue, 17 Dec 2013) | 1 line
	Adding PDF to Spider ON segmentation. Need to try it
r1172 | yben | 2013-12-09 09:45:24 -0600 (Mon, 09 Dec 2013) | 1 line
	Fixing the ON CT segmentation
r1170 | yben | 2013-12-09 09:04:49 -0600 (Mon, 09 Dec 2013) | 1 line
	Changing the regular spider to CT
r1161 | yben | 2013-12-06 15:49:22 -0600 (Fri, 06 Dec 2013) | 2 lines
	little issues with ON_segmentation
r1056 | yben | 2013-11-15 15:32:28 -0600 (Fri, 15 Nov 2013) | 1 line
	Fixing the fix to go from Spider.py to XnatUtils
r1049 | masispider | 2013-11-15 13:35:55 -0600 (Fri, 15 Nov 2013) | 1 line
	Organizing the folder in a better way with the cci package comming out soon. One folder for the processors, one for the modules and one for the spider working with the new way
 
**Current Contact Person**
<date> <name> <email / URL> 

