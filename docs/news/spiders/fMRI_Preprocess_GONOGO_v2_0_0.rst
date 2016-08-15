fMRI_Preprocess_GONOGO_v2_0_0
=============================

* **What does it do?**
Runs SPM fMRI Preprocess from ZALD grp on GONOGO sequences.

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
| GONOGO1
| GONOGO2
| MATLAB

* **References**

* **Version History**

<revision> <name> <date> <lines changed>
r4436 | masispider | 2016-03-27 13:01:49 -0500 (Sun, 27 Mar 2016) | 1 line
    fixed preprocess GONOGO spider
r4434 | masispider | 2016-03-27 12:45:39 -0500 (Sun, 27 Mar 2016) | 1 line
    fixed gonogo preprocess 2
r4433 | masispider | 2016-03-27 12:25:08 -0500 (Sun, 27 Mar 2016) | 1 line
    added fMRI preprocess GONGO v2 spider
 
