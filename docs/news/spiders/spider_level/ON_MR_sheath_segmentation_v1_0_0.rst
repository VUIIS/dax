ON_MR_sheath_segmentation_v1_0_0
================================

* **What does it do?**
Estimates the radius of the optic nerve and surrounding subarachnoid cerebrospinal fluid at each slice which contains optic nerve labels.

* **Data Requirements**
| Heavily T2-weighted 0.6mm isotropic research optic nerve scan
| Completed ON_MR_segmentation with NLSS resource
| Trained random forest from matlab's TreeBagger to transform parameter space to radius space

* **Software Requirements**
| masimatlab utils folder
| ANTS registration (used for resampling)

* **Resources (Outputs)** *
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| CENTROIDS - The centroids before and after smoothing and after fitting
| RADII - The estimated radii of the left and right ON for every iteration
| MATLAB - The matlab script used to run the estimation

**Current Contact Person**
July 2016 Robert L Harrigan `email <mailto:Rob.L.Harrigan@vanderbilt.edu>`_ / `MASI <https://masi.vuse.vanderbilt.edu/index.php/MASI:Rob_Harrigan>`_

* **References**
Harrigan, Robert L., et al. "Disambiguating the optic nerve from the surrounding cerebrospinal fluid: Application to MS‐related atrophy." Magnetic resonance in medicine 75.1 (2016): 414-422.

* **Version History**
<revision> <name> <date> <lines changed> 

