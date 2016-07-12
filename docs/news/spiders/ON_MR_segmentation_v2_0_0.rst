ON_MR_segmentation_v2_0_0
=========================

* **What does it do?**
More flexible version of ON_MR_segmentation which utilizes an atlas definition file to allow for multiple atlases to be used to segment a single project. Each scan type is assigned an atlas directory which is used for multi-atlas segmentation on a cropped region. Cropping is done through a rigid multi-atlas segmentation of the eye globes and padding. 

* **Requirements**
 * masimatlab utilities
 * ANTS registration
 * niftyreg 
 * fsl v5.0
 * mipav v7.0+
 * JIST
 * PICSL MALF jointfusion

* **Resources**
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| JLF - The joint label fusion label result
| NLSS - The NLSS label fusion result
| targets - The cropped image and a mat file with cropping bounds
| non_rigid_registration - The warp and affine transformation outputs from ANTS
| MATLAB - The matlab script used to run the segmentation

* **References**

* **Version History**
<revision> <name> <date> <lines changed>

r4212 | robharrigan | 2016-02-08 11:17:39 -0600 (Mon, 08 Feb 2016) | 1 line
	removing nlss files
r4209 | robharrigan | 2016-02-05 15:06:58 -0600 (Fri, 05 Feb 2016) | 1 line
	updating upload order
r4195 | robharrigan | 2016-02-04 12:34:39 -0600 (Thu, 04 Feb 2016) | 1 line
	renaming resources
r4189 | robharrigan | 2016-02-04 10:11:41 -0600 (Thu, 04 Feb 2016) | 1 line
	fixing upload bug...
r4175 | robharrigan | 2016-01-29 12:23:07 -0600 (Fri, 29 Jan 2016) | 1 line
	bug fixes with JLF addition
r4168 | robharrigan | 2016-01-28 13:59:50 -0600 (Thu, 28 Jan 2016) | 1 line
	adding JLF to spider and processor
r4162 | robharrigan | 2016-01-27 11:44:36 -0600 (Wed, 27 Jan 2016) | 1 line
	updating version name and text flushing
r4128 | robharrigan | 2016-01-25 13:54:47 -0600 (Mon, 25 Jan 2016) | 1 line
	bug fixes for spider
r4089 | robharrigan | 2016-01-13 17:23:49 -0600 (Wed, 13 Jan 2016) | 1 line
	updated niftireg path to add bin
r4080 | robharrigan | 2016-01-12 16:47:35 -0600 (Tue, 12 Jan 2016) | 1 line
	initial add of MR segmentation v2 spider

**Current Contact Person**
<date> <name> <email / URL> 
July 2016 Robert L Harrigan Rob.L.Harrigan@vanderbilt.edu [MASI](https://masi.vuse.vanderbilt.edu/index.php/MASI:Rob_Harrigan)
	
	
