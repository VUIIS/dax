CCI Processes with XNAT
=======================

Table of Contents:
~~~~~~~~~~~~~~~~~~

1.  `Processes <#processes>`__
2.  `AbOrganSeg_Localized_v1`__
3.  `AbOrganSeg_Whole_v1`__
4.  `ASHS_v1`__
5.  `ASLQA_Rest_v1`__
6.  `ASLQA_Task_v1`__
7.  `ASL_RCBF_v0`__
8.  `Bedpost_v1`__
9.  `dtiQA_Amico_Multi_v1`__
10. `dtiQA_Noddi_Multi`__
11. `dtiQA_v2`__
12. `fMRI_Connectivity_PreProcess_Scan_v1`__
13. `fMRI_Connectivity_Process_Scan_v1`__
14. `fMRI_Preprocess`__
15. `fMRIQA`__
16. `FreeSurferRecon_v4`__
17. `FreeSurferSingle_v1`__
18. `FSL_First`__
19. `intra_sess_reg`__
20. `LesionTOADS_v0`__
21. `LST_v1`__
22. `MaCRUISEplus_v0`__
23. `MaCRUISE_v0`__
24. `Multi_Atlas`__
25. `ON_CT_segmentation_v2`__
26. `ON_MR_segmentation`__
27. `ON_MR_segmentation_vDEV1`__
28. `ON_MR_sheath_segmentation`__
29. `Probtrackx2_v1`__
30. `SCFusion_v1`__
31. `SpleenSeg_Localized_v1`__
32. `SUIT_v1`__
33. `SWI_vDEV0`__
34. `TBSS_pre`__
35. `TRACULA_v1`__
36. `VBMQA`__
37. `VBMQA_v1`__
38. `White_Matter_Stamper`__
39. `Optic Nerve and ...`__

---------
Processes
---------

Using XNAT as an imaging storage database and ACCRE as our processing engine, we have developed a python package to facilitate streamlined processing of complex multi-modal MRI and CT data. Many of such processes produce data used for analyses (such as volumetric data). Such resultant data can be pushed to REDCap.
Below is a list of our current processes. The are listed by "proctype" as would be seen in XNAT.

-----------------------
AbOrganSeg_Localized_v1
-----------------------

Purpose
~~~~~~~

This script segments 13 organs on abdominal scans. The organs of interest include (1) spleen; (2) right kidney; (3) left kidney; (4) gallbladder; (5) esophagus; (6) liver; (7) stomach; (8) aorta; (9) inferior vena cava; (10) splenic and portal vein; (11) pancreas; (12) right adrenal gland; (13) left adrenal gland. This pipeline augments "Spider_AbOrganSeg_Whole_v1_0_0.py" by random forest (RF) organ localization. Specifically, each organ is localized within bounding box, based on which an organ-wise region of interest (ROI) is cropped from the CT scan. The multi-atlas framework used in "Spider_AbOrganSeg_Whole_v1_0_0.py" is then applied to each organ-wise ROI. In the end, the segmentation of each organ is transferred back to the original volume space to yield the final result. The atlases consist of 30 manually labeled abdominal CT scans, where each atlas is cropped into 13 organ-wise ROIs. The context models were trained on 30 abdominal scans with 16 tissue types (13 organs of interest, plus fat, muscle, and others). The RF were trained on 10 of the 30 atlases.

Scan Requirements
~~~~~~~~~~~~~~~~~

CT scan of the abdomen

Stats Produced
~~~~~~~~~~~~~~

ROI volumes of the 13 ROIs

References
~~~~~~~~~~

http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4405670/

-------------------
AbOrganSeg_Whole_v1
-------------------

Purpose
~~~~~~~

This script segments 13 organs on abdominal scans. The organs of interest include (1) spleen; (2) right kidney; (3) left kidney; (4) gallbladder; (5) esophagus; (6) liver; (7) stomach; (8) aorta; (9) inferior vena cava; (10) splenic and portal vein; (11) pancreas; (12) right adrenal gland; (13) left adrenal gland. The segmentation follows a multi-atlas segmentation framework. Specifically, it uses NifyReg for registration, SIMPLE context learning for atlas selection, and employs Joint Label Fusion for generating the segmentation for multiple organs. The atlases consist of 10 manually labeled abdominal CT scans. The context models were trained on 30 abdominal scans with 16 tissue types (13 organs of interest, plus fat, muscle, and others).

Scan Requirements
~~~~~~~~~~~~~~~~~

CT scan of the abdomen

Stats Produced
~~~~~~~~~~~~~~

ROI volumes of the 13 organs of interest.

References
~~~~~~~~~~

https://my.vanderbilt.edu/masi/2015/08/efficient-multi-atlas-abdominal-segmentation-on-clinically-acquired-ct-with-simple-context-learning/

-------
ASHS_v1
-------

Purpose
~~~~~~~

Automated Subfield Hippocampal Segmentation (ASHS) performs subfield segmentation of the hippocampus.

Scan Requirements
~~~~~~~~~~~~~~~~~

Both T1 and T2-weighted MR data are required for this process.

Stats Produced
~~~~~~~~~~~~~~

Volumes are produced bilaterally for the following regions of interest:

- CA1
- CA2
- Dentate Gyrus
- CA3
- Hippocampal head
- Hippocampal tail
- "Miscellaneous"
- Subiculum
- Broadman Area 36
- Broadman Area 35
- Collateral Sulcus

References
~~~~~~~~~~

http://onlinelibrary.wiley.com/doi/10.1002/hbm.22627/epdf

-------------
ASLQA_Rest_v1
-------------

Purpose
~~~~~~~

This process registers all of the ASL volumes together and scales the volumes to get absolute CBF. Data is registered to 2mm MNI space and then average values for gray matter are computed. Plots of motion are displayed as well as boxplots of CBF values in the left, right, subcortical and total (sum) regions of the brain of gray matter only.

Scan Requirements
~~~~~~~~~~~~~~~~~

- ASL MR data (control and label only) M0 scan
- T1-weighted MR scan

Stats Produced
~~~~~~~~~~~~~~

CBF values (mean and stddev) in the rh/lh of the brain.

References
~~~~~~~~~~

http://www.ncbi.nlm.nih.gov/pubmed/24715426

-------------
ASLQA_Task_v1
-------------

Purpose
~~~~~~~

Performs similar metrics to that of the resting state version. This process handles the possibility of different gasses being used to induce hypercapnia/hypercarbia. Perfusion is computed for each part of the challenge and displayed for review.

Scan Requirements
~~~~~~~~~~~~~~~~~

- ASL MR scan
- M0 MR scan

Stats Produced
~~~~~~~~~~~~~~

None. This is just for the purposes of visual inspection in its current form.

References
~~~~~~~~~~

http://www.ncbi.nlm.nih.gov/pubmed/24715426

-----------
ASL_RCBF_v0
-----------

Purpose
~~~~~~~

Perform perfusion computation and regional perfusion segmentation based on FreeSurfer ROIs.

Scan Requirements
~~~~~~~~~~~~~~~~~

- ASL MR scan
- M0 MR scan

Stats Produced
~~~~~~~~~~~~~~

Absolute perfusion in ml/100g/min in the gray matter FreeSrufer ROIs.

References
~~~~~~~~~~

http://www.ncbi.nlm.nih.gov/pubmed/24715426

----------
Bedpost_v1
----------

Purpose
~~~~~~~

Wrapper for FSL's Bedpost tool that performs Bayesian estimation of diffusion parameters.

Scan Requirements
~~~~~~~~~~~~~~~~~

Diffusion weighted MR scan

Stats Produced
~~~~~~~~~~~~~~

http://users.fmrib.ox.ac.uk/~behrens/fdt_docs/fdt_bedpost.html

References
~~~~~~~~~~

http://www.fmrib.ox.ac.uk/analysis/techrep/tr03tb1/tr03tb1/

--------------------
dtiQA_Amico_Multi_v1
--------------------

Purpose
~~~~~~~

This process, like NODDI, uses the MATLAB NODDI toolbox. The AMICO model is fit to the diffusion weighted data. This model, unlike NODDI, is quick to fit and is linear unlike many other models attempting to get at tissue microstructure via diffusion data.

Scan Requirements
~~~~~~~~~~~~~~~~~

- HARDI DTI Scan
- DTI Scan

Stats Produced
~~~~~~~~~~~~~~

Orientation dispersion index volume Volumetric fraction volumes

References
~~~~~~~~~~

http://www.sciencedirect.com/science/article/pii/S1053811914008519

-----------------
dtiQA_Noddi_Multi
-----------------

Purpose
~~~~~~~

Fits the NODDI model to HARDI and DTI data. The MATLAB NODDI toolbox is used and the process provides information such as the orientation dispersion index, and volume fractions.

Scan Requirements
~~~~~~~~~~~~~~~~~

- HARDI DTI Scan
- DTI Scan

Stats Produced
~~~~~~~~~~~~~~

ODI volume and volumetric fraction volumes

References
~~~~~~~~~~

http://www.sciencedirect.com/science/article/pii/S1053811912003539

--------
dtiQA_v2
--------

Purpose
~~~~~~~

The purpose of DTIQA is to determine how "usable" the diffusion data is. Briefly, a chi square map by slice and tensor is generated to determine any outlier gradients and or volumes. An assessment of bias is also determined using SIMEX. Registration is also performed to check for intra-scan movement. Finally a tensor map is displayed (with color) to ensure that the diffusion directions were correctly extracted from the file header.

Scan Requirements
~~~~~~~~~~~~~~~~~

Diffusion-weighted MR scan

Stats Produced
~~~~~~~~~~~~~~

- Registration (motion) information for each volume
- Outliers found during tensor fitting

References
~~~~~~~~~~

https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0061737

------------------------------------
fMRI_Connectivity_PreProcess_Scan_v1
------------------------------------

Purpose
~~~~~~~

Performs smoothing across the fMRI volume in preparation for functional connectivity analysis

Scan Requirements
~~~~~~~~~~~~~~~~~

- Functional scan
- Structural scan

Stats Produced
~~~~~~~~~~~~~~

Number of volumes dropped for processing

References
~~~~~~~~~~

None

---------------------------------
fMRI_Connectivity_Process_Scan_v1
---------------------------------

Purpose
~~~~~~~

Performs functional connectivity based on user specified regions from the Multi Atlas pipeline.

Scan Requirements
~~~~~~~~~~~~~~~~~

- Functional scan
- Structural scan

Stats Produced
~~~~~~~~~~~~~~

Connectivity matrices for ROIs

References
~~~~~~~~~~

None

---------------
fMRI_Preprocess
---------------

Purpose
~~~~~~~

With the preprocessing script, the user will basically prepare the fMRI images in a way that can be comparable between all subjects and within each subject. It has the following steps:

- Realign: takes all volumes within a sequence and computes information, one value for each volume, about how each of the volumes has moved in relation to the first image of the sequence. It also reshapes the volumes so they match the first volume and generates a text file with the information on how each volume has moved in relation to the first one.

- Coregister: Since users are going to use the spatial information of the anatomical volume in order to put the functional volumes in the MNI space, users first have to tell spm that their functionals are going to be in relation to the anatomical.

- Normalization: Register the functional volumes in the standard space MNI.

- Smooth: To reduce the noise in the fMRI, applies a gaussian blur to get rid of noisy information and keep the most significant information from the volumes.

Scan Requirements
~~~~~~~~~~~~~~~~~

fMRI scan

Stats Produced
~~~~~~~~~~~~~~

References
~~~~~~~~~~

None

------
fMRIQA
------

Purpose
~~~~~~~

Using SPM, give a general overview as to whether the scan is good, bad, or questionable.

Scan Requirements
~~~~~~~~~~~~~~~~~

Functional scan

Stats Produced
~~~~~~~~~~~~~~

Suggestion as to whether or not the data is usable.

References
~~~~~~~~~~

None

------------------
FreeSurferRecon_v4
------------------

Purpose
~~~~~~~

FreeSurfer is an open source software to process and analyze brain MRI images. The FreeSurfer main page is: http://surfer.nmr.mgh.harvard.edu . FreeSurfer script segments a T1 weighted image into Grey Matter structures. It generates around 100 labels. It also computes the volumes of the different labels and thickness of cortical Gray Matter. If you want to learn more about FreeSurfer, you can read and follow the tutorial: http://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial .

Scan Requirements
~~~~~~~~~~~~~~~~~

T1-weighted MR scan

Stats Produced
~~~~~~~~~~~~~~

LOTS of ROI values including cortical thickness values, volumes for both cortical and subcortical regions, curvature and area values.

References
~~~~~~~~~~

https://www.zotero.org/freesurfer

-------------------
FreeSurferSingle_v1
-------------------

Purpose
~~~~~~~

FreeSurfer is an open source software to process and analyze brain MRI images. The FreeSurfer main page is: http://surfer.nmr.mgh.harvard.edu . FreeSurfer script segments a T1 weighted image into Grey Matter structures. It generates around 100 labels. It also computes the volumes of the different labels and thickness of cortical Gray Matter. If you want to learn more about FreeSurfer, you can read and follow the tutorial: http://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial. This is slightly different than the previous implementation in that it only takes 1 T1 scan and not as many as exist in the session in XNAT.

Scan Requirements
~~~~~~~~~~~~~~~~~

T1-weighted MR scan

Stats Produced
~~~~~~~~~~~~~~

LOTS of ROI values including cortical thickness values, volumes for both cortical and subcortical regions, curvature and area values.

References
~~~~~~~~~~

https://www.zotero.org/freesurfer

---------
FSL_First
---------

Purpose
~~~~~~~

FSL is a comprehensive library of analysis tools for FMRI, MRI and DTI brain imaging data. The main page is the following: http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/ . FIRST is a model-based segmentation/registration tool, module of FSL. The main page is: http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FIRST . FSL_FIRST is an other way to segment a T1 weighted images. Based on their learned models, FIRST searches through linear combinations of shape modes of variation for the most probable shape instance given the observed intensities in a T1-weighted image.

Scan Requirements
~~~~~~~~~~~~~~~~~

T1-weighted MR scan

Stats Produced
~~~~~~~~~~~~~~

ROI volume values for multiple regions of the brain

References
~~~~~~~~~~

http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FIRST

--------------
intra_sess_reg
--------------

Purpose
~~~~~~~

Register all volumes to the T1 in the session.

Scan Requirements
~~~~~~~~~~~~~~~~~

T1 weighted MR scan and any other type of MR scan(s)

Stats Produced
~~~~~~~~~~~~~~

Forwards and backwards transforms for each volume to the T1 space.

References
~~~~~~~~~~

None

--------------
LesionTOADS_v0
--------------

Purpose
~~~~~~~

Performs lesion estimation using the TOADS-CRUISE JIST package: https://www.nitrc.org/projects/toads-cruise/

Scan Requirements
~~~~~~~~~~~~~~~~~

- Structural scan
- T2-weighted scan

Stats Produced
~~~~~~~~~~~~~~

Lesion estimation

References
~~~~~~~~~~

None

------
LST_v1
------

Purpose
~~~~~~~

Performs lesion detection for T2-weighted MR scans. This process is a wrapper for Lesion Segmentation Tool(LST): http://www.applied-statistics.de/lst.html

Scan Requirements
~~~~~~~~~~~~~~~~~

- FLAIR scan
- Structural scan

Stats Produced
~~~~~~~~~~~~~~

Lesion volume

References
~~~~~~~~~~

http://dbm.neuro.uni-jena.de/pdf-files/Schmidt-NI11.pdf

---------------
MaCRUISEplus_v0
---------------

Purpose
~~~~~~~

Carve out the cortical surface in the Multi Atlas segmentation and correct any inconsistencies that arise as a result of surface detection. This process also takes into account lesions to correct for "diseased" brains.

Scan Requirements
~~~~~~~~~~~~~~~~~

- T1-weighted MR scan
- FLAIR MR scan

Stats Produced
~~~~~~~~~~~~~~

Thickness, curvature, and surface area values for each cortical ROI.

References
~~~~~~~~~~

Pending

-----------
MaCRUISE_v0
-----------

Purpose
~~~~~~~

Carve out the cortical surface in the Multi Atlas segmentation and correct any inconsistencies that arise as a result of surface detection. Unlike MaCRUISE_plus, this does not use a FLAIR scan.

Scan Requirements
~~~~~~~~~~~~~~~~~

T1-weighted MR scan

Stats Produced
~~~~~~~~~~~~~~

Thickness, curvature, and surface area values for each cortical ROI.

References
~~~~~~~~~~

Pending

-----------
Multi_Atlas
-----------

Purpose
~~~~~~~

Performs segmentation of cortical and subcortical regions of the brain. Multiple Atlases are used and label fusion is used to resolve "conflicts" that arise when all atlases do not agree on a label for the voxel in question.

Scan Requirements
~~~~~~~~~~~~~~~~~

T1-weighted MR scan

Stats Produced
~~~~~~~~~~~~~~

ROI volumes for over 130 different regions in the brain.

References
~~~~~~~~~~

https://masi.vuse.vanderbilt.edu/index.php/Image_Analysis_Software#Multi-Atlas_Segmentation_Pipeline

---------------------
ON_CT_segmentation_v2
---------------------

Purpose
~~~~~~~

This script is a pipeline to segment the optic nerves , eye balls and the muscles in CT brain images using multi-atlas segmentation. The atlas consists of 33 CT images, and their cropped versions (the ON ROI). Following steps are involved: 1. affine registration and ROI cropping: The atlas images and labels are affinely registered to the test CT image. The test image is then cropped around the ON ROI based on votes of the registered labels. 2. non-rigid registration: The cropped atlas images and labels are registered to the cropped test image using SyN diffeomorphic registration. 3. multi-atlas label fusion: The registered labels are fused to obtain a consensus segmentation using the Non-Local Spatial STAPLE label fusion algorithm. 4. The label fusion estimate is scaled back to original dimensions by adding background.

Scan Requirements
~~~~~~~~~~~~~~~~~

CT scan of the orbits

Stats Produced
~~~~~~~~~~~~~~

Volumes for the optic nerve and muscles.

References
~~~~~~~~~~

http://www.ncbi.nlm.nih.gov/pubmed/26158064

------------------
ON_MR_segmentation
------------------

Purpose
~~~~~~~

Segment the ON, globes and chiasm on a VISTA image. Registers the 35 atlas images in /scratch/mcr/MRONS_atlas/ to the target image using ANTs SyN. Propagates labels using NLSS label fusion to generate a segmentation.

Scan Requirements
~~~~~~~~~~~~~~~~~

VISTA

Stats Produced
~~~~~~~~~~~~~~

NLSS resource contains a label volume

References
~~~~~~~~~~

http://medicalimaging.spiedigitallibrary.org/article.aspx?articleid=1890552&journalid=165

------------------------
ON_MR_segmentation_vDEV1
------------------------

Purpose
~~~~~~~

Segment the ON, globes and chiasm on a VISTA image. Registers the 35 atlas images in /scratch/mcr/MRONS_atlas/ to the target image using ANTs SyN. Propagates labels using NLSS label fusion to generate a segmentation. Only change from ON_MR_segmentation is downsampling to 256x256 in plane is performed if the input image is too large (>512) to avoid computational issue with inhomogeneous data sets.

Scan Requirements
~~~~~~~~~~~~~~~~~

VISTA

Stats Produced
~~~~~~~~~~~~~~

NLSS resource contains a label volume

References
~~~~~~~~~~

http://medicalimaging.spiedigitallibrary.org/article.aspx?articleid=1890552&journalid=165

-------------------------
ON_MR_sheath_segmentation
-------------------------

Purpose
~~~~~~~

Measures ON and surrounding CSF using the results from ON multi atlas segmentation as initialization by fitting an intensity model in the coronal plane.

Scan Requirements
~~~~~~~~~~~~~~~~~

VISTA Completed ON_MR_segmentation

Stats Produced
~~~~~~~~~~~~~~

RADII files: contain the readius measurements CENTROID files: Shows the initialization and final model centroids

References
~~~~~~~~~~

http://onlinelibrary.wiley.com/doi/10.1002/mrm.25613/full

--------------
Probtrackx2_v1
--------------

Purpose
~~~~~~~

Performs probabilistic tractography in FSL5.

Scan Requirements
~~~~~~~~~~~~~~~~~

Diffusion-weighted MR scan

Stats Produced
~~~~~~~~~~~~~~

Seeds from each target to all other ROIs as well as FSLs "BIGGEST" index and BIGGEST NIFTI volume. ROIs include L/R hippocampus, L/R insula, Precuneus, L/R thalamus, and the cingulate.

References
~~~~~~~~~~

http://www.fmrib.ox.ac.uk/analysis/techrep/tr03tb1/tr03tb1/

-----------
SCFusion_v1
-----------

Purpose
~~~~~~~

Performs multi atlas segmentation of the spine.

Scan Requirements
~~~~~~~~~~~~~~~~~

mFFE scan of the spine

Stats Produced
~~~~~~~~~~~~~~

Gray matter volume and white matter volume of the spinal cord.

References
~~~~~~~~~~

https://my.vanderbilt.edu/masi/2014/04/groupwise-multi-atlas-segmentation-of-the-spinal-cords-internal-structure/

----------------------
SpleenSeg_Localized_v1
----------------------

Purpose
~~~~~~~

This pipeline essentially inherits from "Spider_AbOrganSeg_Localized_v1_0_0.py", while tailored for spleen segmentation on abdominal CT scans. The atlases consist of 30 manually labeled abdominal CT scans with their cropped regions of interest for spleens. The pre-trained context model and random forest, and implementation details follow Spider_AbOrganSeg_Localized_v1_0_0.py

Scan Requirements
~~~~~~~~~~~~~~~~~

CT scan of the abdomen

Stats Produced
~~~~~~~~~~~~~~

Spleen volume

References
~~~~~~~~~~

http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4405670/

-------
SUIT_v1
-------

Purpose
~~~~~~~

Performs cerebellum segmentation using the Spatially UnbIased Template.

Scan Requirements
~~~~~~~~~~~~~~~~~

T1-weighted MR scan

Stats Produced
~~~~~~~~~~~~~~

Bilateral ROI values (when applicable) for the following regions:

- I_IV 
- V
- VI
- Vermis_VI
- CrusI
- Vermis_CrusI
- CrusII
- Vermis_CrusII
- VIIb
- Vermis_VIIb
- VIIIa
- Vermis_VIIIa
- Vermis_VIIIb
- VIIIb
- Vermis_IX
- IX
- Vermis_X
- X
- Dentate
- Interposed
- Fastigial

References
~~~~~~~~~~

- http://www.icn.ucl.ac.uk/motorcontrol/imaging/suit.htm
- http://www.icn.ucl.ac.uk/motorcontrol/pubs/Neuroimage_2006.pdf
- http://www.icn.ucl.ac.uk/motorcontrol/pubs/Neuroimage_2009.pdf
- http://www.icn.ucl.ac.uk/motorcontrol/pubs/Neuroimage_dentate_2011.pdf

---------
SWI_vDEV0
---------

Purpose
~~~~~~~

This process performs phase masking of Susceptibility-Weighted Imaging MR data.

Scan Requirements
~~~~~~~~~~~~~~~~~

An SWI scan with both magnitude and phase data

Stats Produced
~~~~~~~~~~~~~~

No stats are generated in this process. Minimum intensity projection data is generated in a sliding 10 window manor (user configurable) which may be helpful looking for microbleeds

References
~~~~~~~~~~

None

--------
TBSS_pre
--------

Purpose
~~~~~~~

Performs Tract-Based Spatial Statistics (TBSS) pre-processing from the FMRIB FSL library. Runs the following FSL commands:

::

	tbss_1_preproc
	tbss_2_reg -T
	tbss_3_postgres -T
	tbss_4_prestats 0.2
	tbss_non_FA AD
	tbss_non_FA RD

Scan Requirements
~~~~~~~~~~~~~~~~~

Diffusion-weighted MR scan.

Stats Produced
~~~~~~~~~~~~~~

No stats are generated for this process as it is used to prepare the group-wise TBSS analysis.

References
~~~~~~~~~~

http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/TBSS/UserGuide

----------
TRACULA_v1
----------

Purpose
~~~~~~~

TRActs Constrained by UnderLying Anatomy (TRACULA) is part of the FreeSurfer neuroimaging toolkit and is used to generate a set of standard (large) white matter tracts.

Scan Requirements
~~~~~~~~~~~~~~~~~

- Diffusion-weighted MR scan
- T1-weighted MR scan

Stats Produced
~~~~~~~~~~~~~~

References
~~~~~~~~~~

https://surfer.nmr.mgh.harvard.edu/fswiki/Tracula

-----
VBMQA
-----

Purpose
~~~~~~~

Performs VBMQA as part of SPM8.

Scan Requirements
~~~~~~~~~~~~~~~~~

T1-weighted MR scan

Stats Produced
~~~~~~~~~~~~~~

Gray matter volume CSF volume White matter volume

References
~~~~~~~~~~

None

--------
VBMQA_v1
--------

Purpose
~~~~~~~

Performs VBMQA using the VBM8 SPM software package.

Scan Requirements
~~~~~~~~~~~~~~~~~

T1-weighted MR scan

Stats Produced
~~~~~~~~~~~~~~

Gray matter volume CSF Volume White matter volume

References
~~~~~~~~~~

None

--------------------
White_Matter_Stamper
--------------------

Purpose
~~~~~~~

The Eve White Matter Spider applies white matter labels to sessions with both an FA map and a T1 multi-atlas segmentation. The Spider works by first rigidly registering the subject's FA volume to the T1 image. The Spider then non-rigidly registers the FA and T1 volumes from the JHU Eve White Matter Atlas. The white-matter labels are then transferred from the Eve Atlas to the regions where the multi-atlas segmentation identified white matters. The labels are then iteratively grown the fill the remaining white-matter space defined by the multi-atlas segmentation.

Scan Requirements
~~~~~~~~~~~~~~~~~

- T1-weighted MR scan
- Diffusion-weighted MR scan

Stats Produced
~~~~~~~~~~~~~~

FA values at the regions defined in the EVE atlas.

References
~~~~~~~~~~

http://proceedings.spiedigitallibrary.org/proceeding.aspx?articleid=2211494

-------------------
Optic Nerve and ...
-------------------

On Segmentation - CT Sessions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script is a pipeline to segment the optic nerves , eye balls and the muscles in CT brain images using multi-atlas segmentation. The atlas consists of 33 CT images, and their cropped versions (the ON ROI). Following steps are involved:

#. affine registration and ROI cropping: The atlas images and labels are affinely registered to the test CT image. The test image is then cropped around the ON ROI based on votes of the registered labels.
#. non-rigid registration: The cropped atlas images and labels are registered to the cropped test image using SyN diffeomorphic registration.
#. multi-atlas label fusion: The registered labels are fused to obtain a consensus segmentation using the Non-Local Spatial STAPLE label fusion algorithm.
#. The label fusion estimate is scaled back to original dimensions by adding background.
