ON_MR_segmentation_v2_2_0
=========================

* **What does it do?**
More flexible version of ON_MR_segmentation which utilizes an atlas definition file to allow for multiple atlases to be used to segment a single project. Each scan type is assigned an atlas directory which is used for multi-atlas segmentation on a cropped region. Cropping is done through a rigid multi-atlas segmentation of the eye globes and padding. 

v2.1 update allows for rerunning of assessors without repeating registrations. The spider checks for the NON_RIGID_REGISTRATION and CROPPED_TARGETS resources and if they are available, uses them. The process will rewarp all of the atlas labels. This is useful for rerunning segmentations with new label sets. Note that a full rerun is possible by deleting all current resources and restarting the process. 

v2.1.1 added the --offline option to allow for running without XNAT.

v2.2 added metrics calculation, creates a second PDF page for metrics QA and adds a METRICS resource with a csv. Note that the metrics PDF page does NOT contain all metrics calculated but is intended to display enough metrics and images for QA purposes. The full set of metrics calculated will be in the csv in the METRICS resource.

Supported metrics are:

- `Orbital volume <http://www.ncbi.nlm.nih.gov/pubmed/3179254>`_
- `Volume crowding index <http://dx.doi.org/10.3174/ajnr.A3029>`_

Muscle metrics, calculated for left/right and superior, inferior, lateral and medial muscles:

- Rectus muscle volume
- Rectus muscle average diameter
- Rectus muscle maximum diameter
- `Barrett index <http://dx.doi.org/10.1590%2FS1807-59322008000300003>`_

Optic Nerve metrics, calculated for left/right optic nerve:

- Length (curved path)
- Traditional length (straight line)
- Volume
- Average cross-sectional area
- Maximum diameter

Globe metrics, calculated for left/right eye globe:

- Globe volume
- Globe diameter


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
| METRICS - contains a csv with the computed metrics

**Current Contact Person**
July 2016 Robert L Harrigan `email <mailto:Rob.L.Harrigan@vanderbilt.edu>`_ / `MASI <https://masi.vuse.vanderbilt.edu/index.php/MASI:Rob_Harrigan>`_

* **References**

* **Version History**
<revision> <name> <date> <lines changed>

 
**Current Contact Person**
<date> <name> <email / URL> 

July 2016 Robert L Harrigan `email <mailto:Rob.L.Harrigan@vanderbilt.edu>`_ / `MASI <https://masi.vuse.vanderbilt.edu/index.php/MASI:Rob_Harrigan>`_
