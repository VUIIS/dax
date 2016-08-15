ON_MR_segmentation_v2_1_0
=========================

* **What does it do?**
More flexible version of ON_MR_segmentation which utilizes an atlas definition file to allow for multiple atlases to be used to segment a single project. Each scan type is assigned an atlas directory which is used for multi-atlas segmentation on a cropped region. Cropping is done through a rigid multi-atlas segmentation of the eye globes and padding. 

v2.1 update allows for rerunning of assessors without repeating registrations. The spider checks for the NON_RIGID_REGISTRATION and CROPPED_TARGETS resources and if they are available, uses them. The process will rewarp all of the atlas labels. This is useful for rerunning segmentations with new label sets. Note that a full rerun is possible by deleting all current resources and restarting the process. 

* **Data Requirements**
| Heavily T2-weighted optic nerve scan
| Atlas directory with image/label pairs in atlas_images and atlas_labels
| An atlas definition file in the top level atlas directory specifying the atlas to be used for each scan type, see the ON_MR_segmentation processor for more information. 

* **Software Requirements**
| masimatlab utilities
| ANTS registration
| niftyreg 
| fsl v5.0
| mipav v7.0+
| JIST
| PICSL MALF jointfusion

* **Resources (Outputs)**
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| JLF - The joint label fusion label result
| NLSS - The NLSS label fusion result
| targets - The cropped image and a mat file with cropping bounds
| non_rigid_registration - The warp and affine transformation outputs from ANTS
| MATLAB - The matlab script used to run the segmentation

**Current Contact Person**
July 2016 Robert L Harrigan `email <mailto:Rob.L.Harrigan@vanderbilt.edu>`_ / `MASI <https://masi.vuse.vanderbilt.edu/index.php/MASI:Rob_Harrigan>`_

* **References**

* **Version History**
<revision> <name> <date> <lines changed>

 
**Current Contact Person**
<date> <name> <email / URL> 

July 2016 Robert L Harrigan `email <mailto:Rob.L.Harrigan@vanderbilt.edu>`_ / `MASI <https://masi.vuse.vanderbilt.edu/index.php/MASI:Rob_Harrigan>`_
