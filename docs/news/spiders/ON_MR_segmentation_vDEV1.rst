ON_MR_segmentation_vDEV1
========================

* **What does it do?**
Segments the eyes, optic nerve and optic chiasm of a research vista scan using multi-atlas segmentation at a downsampled size of 256x256 in plane resolution. 

* **Requirements**
 * masimatlab utilities
 * ANTS registration
 * mipav v7.0+
 * JIST

* **Resources**
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| NIFTI - The downsampled image which was used for segmentation
| NLSS - The final segmentation result (label file)
| MATLAB - The MATLAB script which performed the segmentation

* **References**
Asman, Andrew J., et al. "Robust non-local multi-atlas segmentation of the optic nerve." SPIE Medical Imaging. International Society for Optics and Photonics, 2013.

* **Version History**
<revision> <name> <date> <lines changed>

r3143 | robharrigan | 2015-08-07 08:06:40 -0500 (Fri, 07 Aug 2015) | 1 line
	fixed finding of image (no longer assumes downsampling)
r2960 | bdb | 2015-07-06 10:34:37 -0500 (Mon, 06 Jul 2015) | 1 line
	Add suffix_proc option for dax 0.3.1, also change vX.X.X to vX_X_X
r2655 | yben | 2015-05-11 09:02:40 -0500 (Mon, 11 May 2015) | 1 line
	Switching Modules/Processors/spiders for the version 0.3.0 of dax package (generic functions build in dax)
r2601 | robharrigan | 2015-04-21 12:53:28 -0500 (Tue, 21 Apr 2015) | 1 line
	fixed missing argument
r2583 | robharrigan | 2015-04-17 09:12:28 -0500 (Fri, 17 Apr 2015) | 1 line
	pdb
r2579 | robharrigan | 2015-04-16 08:30:38 -0500 (Thu, 16 Apr 2015) | 1 line
	typo
r2575 | robharrigan | 2015-04-15 11:51:24 -0500 (Wed, 15 Apr 2015) | 1 line
	testing
r2574 | robharrigan | 2015-04-15 11:43:26 -0500 (Wed, 15 Apr 2015) | 1 line
	fixed extra line break
r2541 | robharrigan | 2015-04-06 12:45:21 -0500 (Mon, 06 Apr 2015) | 1 line
	updated ON spider to use the correct pdf
r1992 | yben | 2014-10-16 12:46:53 -0500 (Thu, 16 Oct 2014) | 2 lines
	Removing MASIMATLAB_PATH called from dax and instead getting path from VUIIS_path_settings.py in processors/
	Adding all the path to processors/VUIIS_path_settings.py for each imaging software used.
r1979 | yben | 2014-10-10 15:07:51 -0500 (Fri, 10 Oct 2014) | 2 lines
	Adding "-singleCompThread" to every matlab called from regular spiders.
	Fixing bedpost problem (using fa.nii instead of dti)
r1904 | yben | 2014-08-15 14:44:13 -0500 (Fri, 15 Aug 2014) | 1 line
	Typo error
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
r1754 | yben | 2014-05-28 10:20:24 -0500 (Wed, 28 May 2014) | 1 line
	Fixing issue with NLSS resource upload
r1448 | robharrigan | 2014-02-07 15:11:16 -0600 (Fri, 07 Feb 2014) | 1 line
	vdev1 spider

**Current Contact Person**
<date> <name> <email / URL> 
July 2016 Robert L Harrigan ` email <mailto:Rob.L.Harrigan@vanderbilt.edu>`_ / `MASI <https://masi.vuse.vanderbilt.edu/index.php/MASI:Rob_Harrigan>`_
	
	
