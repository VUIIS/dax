fMRI_Connectivity_PreProcess_Scan_v2_0_0
========================================

What does it do?
----------------

Preprocesses a single functional MRI image series in preparation for functional connectivity analysis. Performs slice timing correction, motion realignment, coregistration to anatomical image, and temporal filtering. Outputs preprocessed fMRI data in the native space, at the fMRI spatial resolution.

Motion, white matter, and CSF time series are removed from the data by regression. The specified bandpass filter is applied to both data and filter matrix prior to regression. (`Behzadi 2007`_, `Hallquist 2013`_).

If scrub_flag set to 1 in the parameter file, include additional delta function regressors in the confound filter matrix to censor the two volumes around every point where motion (FD) or intensity change (DVARS) exceeds the specified threshold (`Power 2012`_, `Muschelli 2014`_).

If gm_flag is set to 1 in the parameter file, include the mean global gray matter signal in the confound filter matrix (`Fox 2009`_, `Murphy 2009`_).


Current Contact Person
----------------------
2016 Aug 15, Baxter P. Rogers (`baxter.rogers@vanderbilt.edu <mailto:baxter.rogers@vanderbilt.edu>`_)


Requirements
------------

Software
~~~~~~~~

* `MATLAB <http://www.mathworks.com/products/matlab/>`_ (tested with r2013a)

* `SPM12 <http://www.fil.ion.ucl.ac.uk/spm/software/spm12/>`_ (tested with r6225)

Data
~~~~

* High resolution T1 weighted anatomical MR image. 3D NIfTI format is required.
	
* Multiatlas assessor applied to the T1 image. The native space segmentation is used (SEG resource).

* Functional MR image series. 4D NIfTI format is required.

  - Required: the ``tr`` parameter of the scan must be the repetition time (volume acquisition time) in msec.

  - Optional: the ``dropvols`` parameter of the scan indicates how many initial volumes will be discarded to account for image saturation. Defaults to 0.

  - Optional: the 'slorder' parameter of the scan to indicate slice order for slice timing correction. May be ``ascending``, ``descending``, ``ascending_interleaved``, ``descending_interleaved``, or ``none``, in SPM12's meaning of the terms. Defaults to ``none``.

* Filtering parameter file ``parameter_files/parameters_connectivity_preprocessing_v2.csv``. Contains parameters (with default values)::

    FD_threshold,0.5	"FD threshold to identify bad volumes"
    DVARS_threshold,5	"DVARS threshold to identify bad volumes"
    bandpasslo_hz,0.01	"Low frequency cutoff for bandpass filter"
    bandpasshi_hz,0.1	"High freq cutoff for bandpass filter"
    n_mot_PCs,6		"Number of PCs of motion parameters to use as confounds (6 to use all)"
    n_motderiv_PCs,6	"Number of PCS of motion derivatives to use as confounds (6 to use all)"
    n_wmcsf_PCs,6	"Number of PCS from the eroded white matter/CSF ROI to use as confounds"
    gm_flag,0		"Set 1 to include mean gray matter signal as a confound"
    scrub_flag,0	"Set 1 to include delta function regressors for bad volumes in confounds"

* Gray matter ROI definition file 'parameter_files/rois_allGM.csv' lists multiatlas ROIs that are included in gray matter.

* White matter / CSF ROI definition file 'parameter_files/rois_WMCSF.csv' lists multiatlas ROIs that are included in white matter / CSF.



Resources
---------

====================   ==========
``MOVEMENT_PARAM``     Text file containing head position estimates relative to first volume. Units are mm (translation) and radians (rotation). Columns are (x trans) (y trans) (z trans) (x rot) (y rot) (z rot)
``ANAT_MASKED``        T1 anatomical image, non-brain removed using multi-atlas result
``ANAT_EDGES``         Edge image of the T1, used for checking coregistration
``FUNC_MEAN``          Mean of all aligned functional volumes
``FUNC_COREG``         Functional images after realignment and coregistration to T1
``FD``                 Framewise displacement estimated per Power 2012
``DVARS``              DVARS estimated per Power 2012
``MULTI_RESAMP``       Multiatlas ROI image resampled to fMRI geometry
``ROI_GM``             Gray matter ROI image
``ROI_WMCSF``          White matter and CSF ROI image
``ROI_WMCSF_ERODED``   Eroded white matter and CSF ROI image
``CONFOUNDS``          Filter matrix (confounds that were removed from data)
``FUNC_FILTERED``      Filtered functional data with confounds removed
``CONN_QA``            Text file of quality parameters
``COREG_CHECK``        Visual check of coregistration quality
``BADVOLS``            Vector indicating "bad" volumes as defined by the provided FD and DVARS thresholds
``OUTLOG``             STDOUT and STDERR from the process on the grid
``PBS``                The DRMAA compliant batch script to run the job
``PDF``                The output PDF file for determining QA status
``SNAPSHOTS``          Thumbnail of the first page of the PDF resource for viewing on XNAT
====================   ==========


References
----------

.. _`Behzadi 2007`:

Behzadi Y, Restom K, Liau J, Liu TT. A component based noise correction method (CompCor) for BOLD and perfusion based fMRI. Neuroimage. 2007 Aug 1;37(1):90-101. Epub 2007 May 3. PubMed PMID: 17560126; PubMed Central PMCID: PMC2214855.

.. _`Fox 2009`:

Fox MD, Zhang D, Snyder AZ, Raichle ME. The global signal and observed anticorrelated resting state brain networks. J Neurophysiol. 2009 Jun;101(6):3270-83. doi: 10.1152/jn.90777.2008. Epub 2009 Apr 1. PubMed PMID: 19339462; PubMed Central PMCID: PMC2694109.

.. _`Hallquist 2013`:

Hallquist MN, Hwang K, Luna B. The nuisance of nuisance regression: spectral misspecification in a common approach to resting-state fMRI preprocessing reintroduces noise and obscures functional connectivity. Neuroimage. 2013 Nov 15;82:208-25. doi: 10.1016/j.neuroimage.2013.05.116. Epub 2013 Jun 6. PubMed PMID: 23747457; PubMed Central PMCID: PMC3759585.

.. _`Murphy 2009`:

Murphy K, Birn RM, Handwerker DA, Jones TB, Bandettini PA. The impact of global signal regression on resting state correlations: are anti-correlated networks introduced? Neuroimage. 2009 Feb 1;44(3):893-905. doi: 10.1016/j.neuroimage.2008.09.036. Epub 2008 Oct 11. PubMed PMID: 18976716; PubMed Central PMCID: PMC2750906.

.. _`Muschelli 2014`:

Muschelli J, Nebel MB, Caffo BS, Barber AD, Pekar JJ, Mostofsky SH. Reduction of motion-related artifacts in resting state fMRI using aCompCor. Neuroimage. 2014 Aug 1;96:22-35. doi: 10.1016/j.neuroimage.2014.03.028. Epub 2014 Mar 18. PubMed PMID: 24657780; PubMed Central PMCID: PMC4043948.

.. _`Power 2012`:

Power JD, Barnes KA, Snyder AZ, Schlaggar BL, Petersen SE. Spurious but systematic correlations in functional connectivity MRI networks arise from subject motion. Neuroimage. 2012 Feb 1;59(3):2142-54. doi: 10.1016/j.neuroimage.2011.10.018. Epub 2011 Oct 14. Erratum in: Neuroimage. 2012 Nov 1;63(2):999. PubMed PMID: 22019881; PubMed Central PMCID: PMC3254728. http://www.ncbi.nlm.nih.gov/pmc/articles/pmid/22019881/



Version History
---------------

r4275 | damons | 2016-02-16 14:35:52 -0600 (Tue, 16 Feb 2016) | 1 line
	reverted changes back and fixed the issue in spider process handler
r4273 | damons | 2016-02-16 14:24:36 -0600 (Tue, 16 Feb 2016) | 1 line
	bug fix for new template
r4038 | damons | 2015-12-17 14:39:45 -0600 (Thu, 17 Dec 2015) | 1 line
	handle string  vs [] for matlab
r4037 | damons | 2015-12-17 14:30:36 -0600 (Thu, 17 Dec 2015) | 1 line
	oops
r4035 | damons | 2015-12-17 13:32:42 -0600 (Thu, 17 Dec 2015) | 1 line
	string variable died
r3839 | damons | 2015-11-16 14:53:10 -0600 (Mon, 16 Nov 2015) | 1 line
	working on abide
r3830 | damons | 2015-11-15 11:01:47 -0600 (Sun, 15 Nov 2015) | 1 line
	new spider (copy of original) but need for quick build

