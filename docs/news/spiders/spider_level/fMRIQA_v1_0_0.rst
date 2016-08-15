fMRIQA_v1_0_0
=============

* **What does it do?**
Performs QA on fMRI data and gives a suggestion as to whether or not the data is usable, unusable or questionable.
A time series of motion is shown as well as an SNR image of the medial slice and a histogram of all SNR.

* **Requirements**
| fMRI scan (resting state or task based) in NIfTI format
| SPM8 or newer
| Matlab R2013a or newer

* **Resources**
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| STATS - Contains stats about the data including snr, drift, fluctuation, rdc, percent of the standard deviation, max translation and rotation. The name of the spider that ran and the version of the spider.
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| STATS
| MATLAB

* **References**
None

* **Version History**
<date> <name> <brief description of change>
 
**Current Contact Person**
<date> <name> <email / URL> 
