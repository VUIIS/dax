SCFusion_v0_0_0
===============

* **What does it do?**
Segments spinal cord MR images using multi atlas algorithms.

* **Current Contact Person**
08-15-2016  Ben Yvernault  b.yvernault@ucl.ac.uk

* **Software Requirements**
    * MATLAB
    * ANTS
    * Java
    * mipav
    * JIST

* **Data Requirements**
Scans, Processors, Accessors that are input.

* **Offline Compliance**
This spider is NOT offline compliant because it uses XnatUtils.download_biggest_resources and
does not accept an '--offline' flag.

* **Resources**
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| MATLAB -
| qa_snapshots -
| QA -
| SEG -
| STATS -
| MATLAB -

* **References**

* **Version History**
<revision> <name> <date> <lines changed>

r2978 | bdb | 2015-07-06 14:20:08 -0500 (Mon, 06 Jul 2015) | 1 line
	Add suffix_proc option for dax 0.3.1, also change vX.X.X to vX_X_X
	
