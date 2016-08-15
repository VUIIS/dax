fMRI_Preprocess
===============

* **What does it do?**
Runs SPM fMRI Preprocess from ZALD grp.

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
| CAP/MID/GONOGO -

* **References**

* **Version History**
<revision> <name> <date> <lines changed>

r2960 | bdb | 2015-07-06 10:34:37 -0500 (Mon, 06 Jul 2015) | 1 line
    Add suffix_proc option for dax 0.3.1, also change vX.X.X to vX_X_X
r2655 | yben | 2015-05-11 09:02:40 -0500 (Mon, 11 May 2015) | 1 line
    Switching Modules/Processors/spiders for the version 0.3.0 of dax package (generic functions build in dax)
r1992 | yben | 2014-10-16 12:46:53 -0500 (Thu, 16 Oct 2014) | 2 lines
    Removing MASIMATLAB_PATH called from dax and instead getting path from VUIIS_path_settings.py in processors/
    Adding all the path to processors/VUIIS_path_settings.py for each imaging software used.
r1979 | yben | 2014-10-10 15:07:51 -0500 (Fri, 10 Oct 2014) | 2 lines
    Adding "-singleCompThread" to every matlab called from regular spiders.
    Fixing bedpost problem (using fa.nii instead of dti)
r1903 | yben | 2014-08-15 11:42:56 -0500 (Fri, 15 Aug 2014) | 2 lines
    Final commit to work with the new package dax.
    Fix some imports for modules/spiders/processors/Xnat_tools (fs)
r1901 | yben | 2014-08-15 09:05:31 -0500 (Fri, 15 Aug 2014) | 4 lines
    Important Commit:
    1) Adding new spiders using the new template
    2) Switching old spiders to new template
    3) Using new package dax
r1622 | yben | 2014-03-25 09:43:23 -0500 (Tue, 25 Mar 2014) | 2 lines
    Removing: cd out of the directory at the end before copying the files.
    Find the error in the file name.
r1613 | yben | 2014-03-24 10:36:34 -0500 (Mon, 24 Mar 2014) | 1 line
    cd out of the directory at the end before copying the files.
r1605 | yben | 2014-03-21 16:11:16 -0500 (Fri, 21 Mar 2014) | 1 line
    Fixing some issues with the uploading
r1487 | masispider | 2014-02-17 09:24:36 -0600 (Mon, 17 Feb 2014) | 1 line
    Little fix for Spider CAP and typo error in dl MAT file for preprocess spider
r1483 | yben | 2014-02-14 15:37:51 -0600 (Fri, 14 Feb 2014) | 1 line
    Name of the resources = scan ID
r1439 | yben | 2014-02-06 13:10:06 -0600 (Thu, 06 Feb 2014) | 2 lines
    Fixing fMRI Preprocess processor on checking the inputs scans/assessor to set status.
    Changing the Spider_fMRI_Preprocess to work with a VBMQA assessor instead of a T1 (could be mroe that one T1 in a session)
r1076 | yben | 2013-11-19 13:50:29 -0600 (Tue, 19 Nov 2013) | 1 line
    fixing error
r1065 | yben | 2013-11-19 10:48:25 -0600 (Tue, 19 Nov 2013) | 1 line
    fixing fMRI preprocess with the T1 input error.
r1060 | yben | 2013-11-18 14:36:59 -0600 (Mon, 18 Nov 2013) | 1 line
    fixing an issue with fMRI_Preprocess
r1056 | yben | 2013-11-15 15:32:28 -0600 (Fri, 15 Nov 2013) | 1 line
    Fixing the fix to go from Spider.py to XnatUtils
r1049 | masispider | 2013-11-15 13:35:55 -0600 (Fri, 15 Nov 2013) | 1 line
    Organizing the folder in a better way with the cci package comming out soon. One folder for the processors, one for the modules and one for the spider working with the new way

