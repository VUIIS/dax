fMRI_Preprocess_MID
===================

* **What does it do?**
Runs SPM fMRI Preprocess from ZALD grp on MID sequences.

* **Current Contact Person**
08-15-2016  Ben Yvernault  b.yvernault@ucl.ac.uk

* **Software Requirements**
    * MATLAB
    * SPM8
    * VBM8

* **Data Requirements**
Scans, Processors, Accessors that are input.

* **Offline Compliance**
This spider is NOT offline compliant because it uses XnatUtils.download_biggest_resources
and does not accept an '--offline' flag.

* **Resources**
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| spmbatch -
| MID1
| MID2
| MID3
| MATLAB

* **References**

* **Version History**

<revision> <name> <date> <lines changed>
r3059 | parvatp | 2015-07-22 11:37:09 -0500 (Wed, 22 Jul 2015) | 1 line
	someone broke this spider. fixing the download scan part
r2960 | bdb | 2015-07-06 10:34:37 -0500 (Mon, 06 Jul 2015) | 1 line
	Add suffix_proc option for dax 0.3.1, also change vX.X.X to vX_X_X
r2655 | yben | 2015-05-11 09:02:40 -0500 (Mon, 11 May 2015) | 1 line
	Switching Modules/Processors/spiders for the version 0.3.0 of dax package (generic functions build in dax)
r2006 | yben | 2014-10-31 09:48:02 -0500 (Fri, 31 Oct 2014) | 1 line
	Adding Spider fMRI Preprocess for cap/gonogo/mid sequences for ZALD. Adding processor as well.

