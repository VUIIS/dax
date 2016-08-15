ON_MR_sheath_segmentation_v2_0_1
================================

* **What does it do?**
Estimates the radius of the optic nerve and surrounding subarachnoid cerebrospinal fluid at each slice which contains optic nerve labels.

v2.0: Iteratively estimates the radius at each slice. Each iteration smooths each parameter with a B-spline. Outliers are reinitialized with the B-spline. The tolerance for outliers and error huberization are iteratively decreased until a smooth solution is converged to. Also now fits a cubic to the centroids to minimize errors from the MAS intialization. 

v2.0.1: Added offline mode allowing for running without XNAT

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
| PARAMETERS - The fit parameters from every iteration
| CENTROIDS - The centroids before and after smoothing and after fitting
| RADII - The estimated radii of the left and right ON for every iteration
| MATLAB - The matlab script used to run the estimation

**Current Contact Person**
July 2016 Robert L Harrigan `email <mailto:Rob.L.Harrigan@vanderbilt.edu>`_ / `MASI <https://masi.vuse.vanderbilt.edu/index.php/MASI:Rob_Harrigan>`_

* **References**
Coming soon!

* **Version History**
<revision> <name> <date> <lines changed> 

