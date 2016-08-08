Cerebellum_Segmentation_v1_0_0
==============================

* **What does it do?**
Segments the vermis and lobules of the cerebellum. First, a multi-atlas segmentation is performed. This segmentation is then refined using graph-cuts.

* **Requirements**

* **Resources** *
| GCO - Graph cut map
| LOGS - Logs of each step of the segmentation
| PROB - Map of graph cut probabilities
| SEGMENTATION - Final label decisions
| STATS - volumes of each cerebellar region of interest
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT

* **References**
- `Automated cerebellar lobule segmentation with application to cerebellar structural analysis in cerebellar disease`_
.. _Automated cerebellar lobule segmentation with application to cerebellar structural analysis in cerebellar disease: http://www.sciencedirect.com/science/article/pii/S1053811915008472

* **Version History**
<revision> <name> <date> <lines changed>

r3847 | plassaaj | 2015-11-16 16:56:30 -0600 (Mon, 16 Nov 2015) | 1 line
	Updates

**Current Contact Person**
<date> <name> <email / URL> 

August 2016 Andrew Plassard `email <mailto:Andrew.J.Plassard@vanderbilt.edu>`_ / `MASI <https://masi.vuse.vanderbilt.edu/index.php/MASI:Andrew_Plassard>`_
	
	
