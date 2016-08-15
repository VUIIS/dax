ON_MR_segmentation_v1_0_0
==================

* **What does it do?**
Segments the eyes, optic nerve and optic chiasm of a research vista scan using multi-atlas segmentation. 

* **Data Requirements**
| Heavily T2-weighted optic nerve scan
| Atlas directory with image/label pairs in atlas_images and atlas_labels

* **Software Requirements**
| masimatlab utilities
| ANTS registration
| mipav v7.0+
| JIST

* **Resources (Outputs)**
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| NLSS - The final segmentation result (label file)
| MATLAB - The MATLAB script which performed the segmentation

* **Current Contact Person**
August 2016 Robert L Harrigan `email <mailto:Rob.L.Harrigan@vanderbilt.edu>`_ / `MASI <https://masi.vuse.vanderbilt.edu/index.php/MASI:Rob_Harrigan>`_

* **References**
Asman, Andrew J., et al. "Robust non-local multi-atlas segmentation of the optic nerve." SPIE Medical Imaging. International Society for Optics and Photonics, 2013.

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
r1916 | yben | 2014-09-09 14:08:57 -0500 (Tue, 09 Sep 2014) | 1 line
	Debugging....
r1903 | yben | 2014-08-15 11:42:56 -0500 (Fri, 15 Aug 2014) | 2 lines
	Final commit to work with the new package dax.
	Fix some imports for modules/spiders/processors/Xnat_tools (fs)
r1901 | yben | 2014-08-15 09:05:31 -0500 (Fri, 15 Aug 2014) | 4 lines
	Important Commit:
	1) Adding new spiders using the new template
	2) Switching old spiders to new template
	3) Using new package dax
r1824 | yben | 2014-06-10 11:39:24 -0500 (Tue, 10 Jun 2014) | 1 line
	Switching print to sys.stdout.write to see outlog from spider and matlab in the right order
r1822 | yben | 2014-06-10 10:23:36 -0500 (Tue, 10 Jun 2014) | 1 line
	Adding ext matlab path to the pdf maker
r1806 | yben | 2014-06-04 11:06:12 -0500 (Wed, 04 Jun 2014) | 1 line
	removing unzipping the nifti to create pdf
r1513 | yben | 2014-02-21 11:51:36 -0600 (Fri, 21 Feb 2014) | 1 line
	Full path instead of just filename
r1510 | yben | 2014-02-20 09:34:01 -0600 (Thu, 20 Feb 2014) | 1 line
	converting tabs to 4 spaces
r1504 | yben | 2014-02-19 09:02:54 -0600 (Wed, 19 Feb 2014) | 1 line
	Error in the filename. After gzipping, need to add .gz to the name.
r1494 | yben | 2014-02-18 10:53:52 -0600 (Tue, 18 Feb 2014) | 1 line
	Fix a typo error
r1446 | yben | 2014-02-07 09:54:57 -0600 (Fri, 07 Feb 2014) | 1 line
	saving the output as a file now and not a folder. Gzip the file if not gzip
r1366 | yben | 2014-01-27 11:38:53 -0600 (Mon, 27 Jan 2014) | 1 line
	removing display
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
r1162 | yben | 2013-12-06 15:52:30 -0600 (Fri, 06 Dec 2013) | 1 line
	adding spider On segmentation on MR session


	
	
